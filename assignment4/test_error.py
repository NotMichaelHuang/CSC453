from libTinyFS import *


def print_header(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)

def test_errors():
    print_header("ERROR CONDITIONS: Mounting Nonexistent Disk (should fail)")
    x = tfs_mount("no_such_file")
    print(f"tfs_mount('no_such_file') returned {x} (expected -2)")

    print_header("ERROR CONDITIONS: Unmount Without Mount (should fail)")
    x = tfs_unmount()
    print(f"tfs_unmount() returned {x} (expected -1)")

    print_header("ERROR CONDITIONS: Open Without Mount (should fail)")
    x = tfs_open("x")
    print(f"tfs_open('x') returned {x} (expected -1)")

    print_header("ERROR CONDITIONS: Write Without Open (should fail)")
    buf = b"Test"
    x = tfs_write(5, buf, len(buf))
    print(f"tfs_write(5, 'Test', 4) returned {x} (expected -1)")

    print_header("ERROR CONDITIONS: Read Without Open (should fail)")
    tmp = bytearray(1)
    x = tfs_readByte(5, tmp)
    print(f"tfs_readByte(5) returned {x} (expected -1)")

    print_header("ERROR CONDITIONS: Seek Without Open (should fail)")
    x = tfs_seek(5, 0)
    print(f"tfs_seek(5, 0) returned {x} (expected -1)")

    print_header("ERROR CONDITIONS: Delete Without Open (should fail)")
    x = tfs_delete(5)
    print(f"tfs_delete(5) returned {x} (expected -1)")

