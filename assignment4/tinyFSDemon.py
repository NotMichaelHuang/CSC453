#!/usr/bin/env python3
from test_error import test_errors
from test_flow import test_flow


def main():
    default_disk_name = "tinyFSDisk"
    default_disk_size = 10240 # Shape: 40 x 256

    while(True):
        print("\nOptions:")
        print("1. Test Flow of TinyFS")
        print("2. Test Error of TinyFS")
        print("3. Quit")
        user_input = int(input())
        if user_input == 1:
            test_flow(default_disk_name, default_disk_size)
        elif user_input == 2:
            test_errors()
        else:
            break

    

if __name__ == "__main__":
    main() 
 

