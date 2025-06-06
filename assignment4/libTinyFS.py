import os
from typing import Union, List
from libDisk import *

BLOCKSIZE = 256
MAGIC_NUMBER = 0x5A # Our file system signature
DEFAULT_DISK_SIZE = 10240 # 40 blocks of 256 bytes by default
DEFAULT_DISK_NAME = "tinyFSDisk"

# In‐memory globals after mounting
mounted_disk = None # file object returned by openDisk
mounted = False
superblock = bytearray(BLOCKSIZE)
file_table = {} # maps fd -> {"inode_block": int, "pointer": int}
next_fd = 1

# Disk layout (flat namespace):
#   Block 0 = Superblock
#   Block 1 = Root directory (holds name→inode mappings)
#   Blocks 2->N = Inode blocks and data blocks (allocated dynamically)
SUPERBLOCK_BLOCK_NUM = 0
ROOT_DIR_BLOCK_NUM  = 1

# Each directory entry in block 1 is 9 bytes:
#   Bytes [0]       : uint8 count of entries
#   Bytes [1..252]  : up to 28 entries of 9 bytes each
#     - Bytes [entry_offset .. entry_offset+7] = filename (8 bytes, ASCII, padded with 0x00)
#     - Byte  [entry_offset+8]                 = inode_block_num (uint8)
#   Bytes [253..255] = reserved

def _total_blocks() -> int:
    """
        Return the total number of blocks on the mounted disk.
    """
    mounted_disk.seek(0, os.SEEK_END) # Move to the end of the file
    total_bytes = mounted_disk.tell() # Return the total byte from the start to the cursor
    return total_bytes // BLOCKSIZE

def _bitmap_size_bytes(total_blocks: int) -> int:
    """
        Return how many bytes are needed to store total_blocks of bits.
    """
    result = (total_blocks + 7) // 8 # Round up
    return result

def _read_superblock_bitmap() -> bytearray:
    """
        Read and return the free‐block bitmap from superblock (block 0).
        Returns a bytearray of length _bitmap_size_bytes(total_blocks).
    """
    sb_buf = readBlockAsBytes(0, mounted_disk)
    total_blocks = _total_blocks()
    bmp_size = _bitmap_size_bytes(total_blocks)
    return sb_buf[4 : 4 + bmp_size] # Again, 4 is housing the magic number, root inode ptr, etc.

def _write_superblock_bitmap(bitmap: bytearray) -> None:
    """
        Write the given bytearray 'bitmap' into the superblock (block 0) at bytes [4: ...].
        We are updating the superblock...
    """
    sb_buf = bytearray(BLOCKSIZE)
    readBlock(mounted_disk, 0, sb_buf)
    total_blocks = _total_blocks()
    bmp_size   = _bitmap_size_bytes(total_blocks)
    sb_buf[4 : 4 + bmp_size] = bitmap
    writeBlock(mounted_disk, 0, sb_buf)

def _mark_block_used(bitmap: bytearray, block: int) -> None:
    """
        Mark block number 'block' as used (clear its bit to 0) in the given bitmap bytearray.
    """
    byte_index = block // 8 # Find out which byte in the bitmap contains the bit in this block
    bit_index  = block % 8 # Which bit in the byte

    # Mark the bit as used or 0...
    bitmap[byte_index] &= ~(1 << bit_index)

def _mark_block_free(bitmap: bytearray, block: int) -> None:
    """
        Mark block number 'block' as free (set its bit to 1) in the given bitmap bytearray.
    """
    byte_index = block // 8
    bit_index  = block % 8

    # Release bit or 1... brings me back, lol
    bitmap[byte_index] |= (1 << bit_index)

def _get_next_free_block() -> Union[int, bytearray]:
    """
        Scan the free‐block bitmap and return the first free block number >= 2 
        (0 and 1 belongs to superblock and root...). Marks that block used in 
        the bitmap and writes back to superblock. Returns block number on success, 
        or -1 if none available.
    """
    total_blocks = _total_blocks()
    bitmap = _read_superblock_bitmap()
    for block in range(2, total_blocks):
        byte_index = block // 8
        bit_index  = block % 8

        # Is it really free? 
        if (bitmap[byte_index] >> bit_index) & 1:
            _mark_block_used(bitmap, block)
            _write_superblock_bitmap(bitmap)
            return block
    return -1


# Where it all begins
def tfs_mkfs(filename: str, nBytes: int) -> int:
    """
        Format a TinyFS image 'filename' of exactly nBytes (multiple of BLOCKSIZE).
        Sets up:
            - superblock (block 0) with magic number, root‐dir pointer, free‐block bitmap
            - root directory (block 1) as empty (all zeroes)
    """
    global mounted

    if nBytes <= 0 or (nBytes % BLOCKSIZE) != 0:
        return -1  # invalid size

    disk = openDisk(filename, nBytes)
    if disk in (-1, -2):
        return -2  # I/O error

    total_blocks = nBytes // BLOCKSIZE
    zero = bytearray(BLOCKSIZE)

    # Zero out all blocks
    for i in range(total_blocks):
        writeBlock(disk, i, zero)

    # Create superblock (block 0)
    sb = bytearray(BLOCKSIZE)
    sb[0] = MAGIC_NUMBER
    sb[1] = ROOT_DIR_BLOCK_NUM   # pointer to root directory
    # reserved (unused) for now...
    sb[2] = 0
    sb[3] = 0

    # Initialize free‐block bitmap: 1 bit per block
    bmp_size = _bitmap_size_bytes(total_blocks)
    bitmap = bytearray(bmp_size)

    # Mark all blocks free initially
    for block in range(total_blocks):
        _mark_block_free(bitmap, block)

    # Reserve blocks 0 (superblock) and 1 (root directory)
    _mark_block_used(bitmap, 0)
    _mark_block_used(bitmap, 1)
    sb[4 : 4 + bmp_size] = bitmap

    writeBlock(disk, 0, sb)

    # Write an empty root directory (block 1)
    root_dir = bytearray(BLOCKSIZE)

    # root_dir[0] = 0  # no entries
    writeBlock(disk, ROOT_DIR_BLOCK_NUM, root_dir)

    closeDisk(disk)
    return 0

def tfs_mount(filename: str) -> int:
    """
        Mount the TinyFS image in 'filename'. Reads superblock, checks magic number,
        and caches the 256‐byte superblock in the global 'superblock' for later writes.
    """
    global mounted, mounted_disk, superblock

    if mounted:
        return -1  # already mounted

    disk = openDisk(filename, 0)
    if disk in (-1, -2):
        return -2  # I/O error / no file

    sb_buf = bytearray(BLOCKSIZE)
    if readBlock(disk, 0, sb_buf) != 0 or sb_buf[0] != MAGIC_NUMBER:
        print("Mount failed: Invalid superblock or not a TinyFS image")
        closeDisk(disk)
        return -3  # not a valid TinyFS image

    superblock[:] = sb_buf # Update global superblock
    mounted_disk = disk # BinaryIO
    mounted = True
    return 0

def tfs_unmount() -> int:
    """
        Unmount the currently mounted TinyFS. Writes the in‐memory superblock back to block 0,
        closes the disk file, clears the open‐file table, and resets 'mounted'.
    """
    global mounted, mounted_disk, superblock, file_table

    if not mounted:
        return -1 # Already unmounted

    writeBlock(mounted_disk, 0, superblock) # Save the changes to sb
    closeDisk(mounted_disk)
    mounted_disk = None
    file_table.clear() # return an empty dic
    mounted = False
    return 0

def tfs_open(name: str) -> int:
    """
        Open a file by name in the root directory. If it exists, return a new fd.
        If it does not exist, allocate:
            - a new inode block (via _get_next_free_block())
            - add an entry into the root directory (block 1)
        Returns file descriptor >= 1 on success, or negative error code:
            -1 if not mounted
            -2 if directory full or no free inode
            -3 if name too long (>8)
    """
    global next_fd, file_table

    if not mounted:
        return -1

    # As per specification for the name only length of 8
    if len(name) > 8:
        return -3

    # Read root directory (block 1)
    root_dir = readBlockAsBytes(1, mounted_disk)
    if root_dir is None:
        return -2
 
    # Search for existing entry
    count = root_dir[0]
    for i in range(count):
        offset = 1 + i * 9
        raw_name = bytes(root_dir[offset : offset + 8])
        entry_name = raw_name.rstrip(b'\x00').decode() # Remove the padding and covert to str
        inode_block = root_dir[offset + 8]
        if entry_name == name:
            # Found existing file → create fd
            fd = next_fd
            next_fd += 1
            file_table[fd] = {"inode_block": inode_block, "pointer": 0}
            return fd

    # Not found, then allocate a new inode
    inode_block = _get_next_free_block()
    if inode_block < 0:
        return -2  # no free blocks for inode

    # Initialize the inode block: mark in use, size=0, data_block=0
    inode_buf = bytearray(BLOCKSIZE)
    inode_buf[0] = 1 # in use
    inode_buf[1:3] = (0).to_bytes(2, 'big')  # file size = 0 and standard choice for disk
    inode_buf[3] = 0 # no data block yet
    writeBlock(mounted_disk, inode_block, inode_buf)

    # Add new directory entry into block 1
    if count >= 28:
        return -2  # directory is full (max 28 entries)

    new_offset = 1 + count * 9
    root_dir[new_offset : new_offset + 8] = name.encode().ljust(8, b'\x00')
    root_dir[new_offset + 8] = inode_block
    root_dir[0] = count + 1
    writeBlock(mounted_disk, 1, root_dir)

    # Create and return file descriptor
    fd = next_fd
    next_fd += 1
    file_table[fd] = {"inode_block": inode_block, "pointer": 0}
    return fd

def tfs_close(fd: int) -> int:
    """
        Close the file descriptor `fd`. Simply remove it from the open‐file table.
        Returns 0 on success, or -1 if fd is invalid/not open.
    """
    if not mounted or fd not in file_table:
        return -1
    del file_table[fd]
    return 0

def tfs_write(fd: int, data: bytearray, size: int):
    """
        Write exactly `size` bytes from `data` into the file represented by `fd`.
        Steps:
            1) Read that file’s inode to get existing data block (if any).
            2) If no data block, allocate a new block via _get_next_free_block().
            3) Write up to BLOCKSIZE bytes into the data block.
            4) Update inode: set in‐use, file size, data block pointer.
            5) Ensure bitmap marks data block as used.
        Returns 0 on success, or negative error:
            -1 if invalid fd/not mounted
            -2 if cannot allocate data block
    """
    if not mounted or fd not in file_table:
        return -1

    entry = file_table[fd]
    inode_block = entry["inode_block"]

    # Load inode
    inode_buf = bytearray(BLOCKSIZE)
    readBlock(mounted_disk, inode_block, inode_buf)

    # Determine data block
    data_block = inode_buf[3]
    if data_block == 0:

        # Need to allocate a data block
        data_block = _get_next_free_block()
        if data_block < 0:
            return -2  # no free block for data

    # Write data into data block
    buf = bytearray(BLOCKSIZE)

    # Make sure it's bytearray
    data_bytes = data.encode() if isinstance(data, str) else data
    actual_len = min(size, len(data_bytes), BLOCKSIZE)
    buf[:actual_len] = data_bytes[:actual_len]
    writeBlock(mounted_disk, data_block, buf)

    # Update inode: mark “in use,” store file size, store data block
    inode_buf[0] = 1
    inode_buf[1:3] = actual_len.to_bytes(2, 'big')
    inode_buf[3] = data_block
    writeBlock(mounted_disk, inode_block, inode_buf)

    # Ensure bitmap marks data_blk used (inode_blk already marked used at creation)
    bmp = _read_superblock_bitmap()
    _mark_block_used(bmp, data_block)
    _write_superblock_bitmap(bmp)

    entry["pointer"] = 0
    return 0

def tfs_readByte(fd: int, buffer: bytearray) -> int:
    """
        Read one byte from the file at `fd` at its current pointer:
            - Copy byte into buffer[0]
            - Increment the pointer
            - Return 0 on success, -2 if at EOF, -1 if invalid fd
    """
    if not mounted or fd not in file_table:
        return -1

    entry = file_table[fd]
    inode_block = entry["inode_block"]
    pointer = entry["pointer"]

    # Load inode
    inode_buf = bytearray(BLOCKSIZE)
    readBlock(mounted_disk, inode_block, inode_buf)
    file_size = int.from_bytes(inode_buf[1:3], 'big') # Convert 2 bytes
    data_blk = inode_buf[3]

    if pointer >= file_size:
        return -2  # EOF

    # Read data block
    data_buf = bytearray(BLOCKSIZE)
    readBlock(mounted_disk, data_blk, data_buf)
    buffer[0] = data_buf[pointer]
    entry["pointer"] += 1
    return 0

def tfs_seek(fd: int, offset: int) -> int:
    """
        Move the file pointer for `fd` to absolute `offset`.
        Return 0 on success, -2 if offset ≥ file_size, -1 if invalid fd.
    """
    if not mounted or fd not in file_table:
        return -1

    entry = file_table[fd]
    inode_block = entry["inode_block"]
    inode_buf = bytearray(BLOCKSIZE)
    readBlock(mounted_disk, inode_block, inode_buf)
    file_size = int.from_bytes(inode_buf[1:3], 'big')

    if offset >= file_size:
        return -2

    entry["pointer"] = offset
    return 0

def tfs_delete(fd: int) -> int:
    """
        Delete the file referenced by `fd`:
            - Remove its directory entry from block 1
            - Read its inode to find data block, zero out both inode & data blocks
            - Mark both blocks free in bitmap
            - Remove fd from file_table
        Returns 0 on success, -1 if invalid fd.
    """
    if not mounted or fd not in file_table:
        return -1

    inode_block = file_table[fd]["inode_block"]

    # Remove directory entry from root (block 1)
    root_dir = readBlockAsBytes(1, mounted_disk)
    count = root_dir[0]
    for i in range(count):
        offset = 1 + (i * 9)
        entry_inode = root_dir[offset + 8]
        if entry_inode == inode_block:
            # Shift subsequent entries up
            for j in range(i, count - 1):
                src = 1 + (j+1) * 9
                dst = 1 + j * 9
                root_dir[dst : dst + 9] = root_dir[src : src + 9]
            # Zero out the last entry
            last_offset = 1 + (count - 1) * 9
            root_dir[last_offset : last_offset + 9] = b'\x00' * 9
            root_dir[0] = count - 1
            writeBlock(mounted_disk, 1, root_dir)
            break

    # Load the inode to find its data block
    inode_buf = readBlockAsBytes(inode_block, mounted_disk)
    data_blk = inode_buf[3]

    # Zero out inode block and data block
    zero = bytearray(BLOCKSIZE)
    writeBlock(mounted_disk, inode_block, zero)
    if data_blk != 0:
        writeBlock(mounted_disk, data_blk, zero)

    # Mark both blocks free in the bitmap
    bmp = _read_superblock_bitmap()
    _mark_block_free(bmp, inode_block)
    if data_blk != 0:
        _mark_block_free(bmp, data_blk)
    _write_superblock_bitmap(bmp)

    # Remove from file_table
    del file_table[fd]
    return 0

def tfs_readdirnames() -> Union[int, List[str]]:
    """
        List all filenames in the root directory. Returns -1 if error.
    """
    if not mounted:
        return -1

    root_dir = readBlockAsBytes(1, mounted_disk)
    count = root_dir[0]
    names = []
    for i in range(count):
        offset = 1 + i * 9
        raw_name = bytes(root_dir[offset : offset+8])
        name = raw_name.rstrip(b'\x00').decode()
        names.append(name)
    return names

def tfs_rename(oldName: str, newName: str) -> int:
    """
        Rename a file in the root directory from oldName → newName.
        Returns 0 on success, or:
            -1 if not mounted
            -2 if oldName not found
            -3 if newName too long (>8) or already exists
    """
    if not mounted:
        return -1

    # Can't bee too careful
    if len(newName) > 8:
        return -3

    root_dir = readBlockAsBytes(1, mounted_disk)
    count = root_dir[0]
    found = -1

    for i in range(count):
        offset = 1 + i*9
        raw_name = bytes(root_dir[offset : offset+8])
        name    = raw_name.rstrip(b'\x00').decode()
        if name == newName:
            return -3  # newName already in use
        if name == oldName:
            found = i

    if found < 0:
        return -2  # oldName not found

    # Overwrite the 8 bytes at that entry with newName
    offset = 1 + found * 9
    root_dir[offset : offset + 8] = newName.encode().ljust(8, b'\x00')
    writeBlock(mounted_disk, 1, root_dir)
    return 0

def tfs_displayFragment() -> int:
    """
        Print a map of all blocks (0 .. total_blocks-1), marking each 'Used' or 'Free'
        based on the free-block bitmap stored in superblock.
    """
    if not mounted:
        print("Error: No TinyFS mounted.")
        return -1

    total_blocks = _total_blocks()
    bmp_size = _bitmap_size_bytes(total_blocks)
    sb_buf = bytearray(BLOCKSIZE)
    readBlock(mounted_disk, 0, sb_buf)

    free_bitmap = sb_buf[4 : 4 + bmp_size]
    print(f"Block usage map (0 ... {total_blocks - 1}):")
    for block in range(total_blocks):
        byte_index = block // 8
        bit_index = block % 8
        is_free = (free_bitmap[byte_index] >> bit_index) & 1
        status = "Free" if is_free else "Used"
        print(f"  Block {block:02}: {status}")

    return 0

def tfs_defrag() -> int:
    """
        Compact all data blocks so they follow immediately after the last inode.
        Updates each inode’s data-block pointer and the free-block bitmap accordingly.
        In a multi-file FS, sorts inodes by their data-block, moves content, updates pointers.
    """
    if not mounted:
        print("Error: No TinyFS mounted.")
        return -1
 
    # Collect all in-use inodes (block >= 2 with byte 0 == 1)
    total_blocks = _total_blocks()
    inodes = []  # list of tuples (inode_block, data_block)
    for block in range(2, total_blocks):
        buf = readBlockAsBytes(block, mounted_disk)
        if buf is None:
            continue
        if buf[0] == 1:
            data_blk = buf[3]
            if data_blk != 0:
                inodes.append((block, data_blk))

    if not inodes:
        return 0  # nothing to defrag

    # Determine first free data target: one after the highest inode block
    max_inode_blk = max(inode_block for (inode_block, _) in inodes)
    next_data_target = max_inode_blk + 1

    # Sort inodes by current data block (ascending)
    inodes.sort(key=lambda x: x[1])

    # Read bitmap once
    free_bitmap = _read_superblock_bitmap()

    # Move each data block if necessary
    for (inode_blk, old_data_blk) in inodes:
        # If old_data_blk < next_data_target, skip (either already moved earlier or in place)
        if old_data_blk < next_data_target:
            next_data_target = old_data_blk + 1
            continue
        # If old_data_blk == next_data_target, it’s already in correct place
        if old_data_blk == next_data_target:
            next_data_target += 1
            continue

        # Move data: read old, write to new
        data_buf = readBlockAsBytes(old_data_blk, mounted_disk)
        if data_buf is None:
            print(f"Error: Cannot read data block {old_data_blk}")
            return -2
        write_status = writeBlock(mounted_disk, next_data_target, data_buf)
        if write_status != 0:
            print(f"Error: Cannot write to block {next_data_target}")
            return -3

        # Zero out old block
        zero_buf = bytearray(BLOCKSIZE)
        writeBlock(mounted_disk, old_data_blk, zero_buf)

        # Update inode’s pointer (byte 3)
        inode_buf = readBlockAsBytes(inode_blk, mounted_disk)
        if inode_buf is None:
            print(f"Error: Cannot re-read inode {inode_blk}")
            return -4
        inode_buf[3] = next_data_target
        writeBlock(mounted_disk, inode_blk, inode_buf)

        # Update bitmap: mark new used, old free
        _mark_block_used(free_bitmap, next_data_target)
        _mark_block_free(free_bitmap, old_data_blk)
        _write_superblock_bitmap(free_bitmap)

        next_data_target += 1

    return 0
