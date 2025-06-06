from libTinyFS import *


def print_header(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)

def test_flow(disk_name, size):
    print_header("STEP 1: Format & Mount Disk")
    x = tfs_mkfs(disk_name, size)
    print(f"tfs_mkfs returned {x} (expected 0)")
    x = tfs_mount(disk_name)
    print(f"tfs_mount returned {x} (expected 0)")

    print_header("STEP 2: Initial Fragmentation Map")
    tfs_displayFragment()

    print_header("STEP 3: Initial Directory Listing (should be empty)")
    names = tfs_readdirnames()
    print(f"tfs_readdir() returned {names} (expected [])")

    print_header("STEP 4: Create file 'test1' and write 50 bytes")
    fd_test1 = tfs_open("test1")
    print(f"tfs_open('test1') returned fd = {fd_test1}")
    data_test1 = b"Let me die" * 5
    x = tfs_write(fd_test1, data_test1, len(data_test1))
    print(f"tfs_write(test1, 50 bytes) returned {x} (expected 0)")

    print_header("STEP 5: Create file 'test2' and write 80 bytes")
    fd_test2 = tfs_open("test2")
    print(f"tfs_open('test2') returned fd = {fd_test2}")
    data_test2 = b"Living is suffering, suffering is living" * 2
    x = tfs_write(fd_test2, data_test2, len(data_test2))
    print(f"tfs_write(test2, 80 bytes) returned {x} (expected 0)")

    print_header("STEP 6: Fragmentation Map After Writing 'test1' & 'test2'")
    tfs_displayFragment()

    print_header("STEP 7: Directory Listing After Creating Two Files")
    names = tfs_readdirnames()
    print(f"tfs_readdir() returned {names} (expected ['test1','test2'])")

    print_header("STEP 8: Read first 10 bytes from 'test1'")
    x = tfs_seek(fd_test1, 0)
    print(f"tfs_seek(test1,0) returned {x} (expected 0)")
    buf = bytearray(1)
    print("Data read from 'test1':", end=" ")
    for i in range(10):
        x = tfs_readByte(fd_test1, buf)
        if x == 0:
            print(chr(buf[0]), end="")
        else:
            print(f"\n  tfs_readByte returned {x} at i={i}")
            break
    print()

    # Rename
    print_header("STEP 9: Rename 'test1' -> 'one_test'")
    x = tfs_rename("test1", "one_test")
    print(f"tfs_rename('test1','one_test') returned {x} (expected 0)")

    print_header("STEP 10: Directory Listing After Rename")
    names = tfs_readdirnames()
    print(f"tfs_readdir() returned {names} (expected ['one_test','test2'])")

    # Attempt to rename non‐existent file
    print_header("STEP 11: Attempt to Rename 'hello' -> 'world' (should fail)")
    x = tfs_rename("hello", "world")
    print(f"tfs_rename('hello',' world') returned {x} (expected -2)")

    # Overwrite 'beta' with new data
    print_header("STEP 12: Overwrite 'test2' with 20 bytes 'A'")
    fd_test2 = tfs_open("test2")  # reopen existing
    data_test2 = b"A" * 20
    x = tfs_write(fd_test2, data_test2, len(data_test2))
    print(f"tfs_write(test2, 20 bytes) returned {x} (expected 0)")

    # Defragment and show fragmentation map
    print_header("STEP 13: Run Defrag")
    x = tfs_defrag()
    print(f"tfs_defrag() returned {x} (expected 0)")
    print("Fragmentation after defrag:")
    tfs_displayFragment()

    # Delete 'test2'
    print_header("STEP 14: Delete 'test2'")
    fd_test2 = tfs_open("test2")
    x = tfs_delete(fd_test2)
    print(f"tfs_delete('test2') returned {x} (expected 0)")

    print_header("STEP 15: Directory Listing After Deleting 'test2'")
    names = tfs_readdirnames()
    print(f"tfs_readdir() returned {names} (expected ['one_test'])")

    # Delete 'one_test'
    print_header("STEP 16: Delete 'one_test'")
    fd_one_test = tfs_open("one_test")
    x = tfs_delete(fd_one_test)
    print(f"tfs_delete('one_test') returned {x} (expected 0)")

    print_header("STEP 17: Directory Listing After Deleting 'one_test'")
    names = tfs_readdirnames()
    print(f"tfs_readdir() returned {names} (expected [])")

    # Final fragmentation map
    print_header("STEP 18: Final Fragmentation Map")
    tfs_displayFragment()

    # Unmount
    print_header("STEP 19: Unmount Disk")
    x = tfs_unmount()
    print(f"tfs_unmount() returned {x} (expected 0)")

