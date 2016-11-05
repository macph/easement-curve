# MIT License, copyright Ewan Macpherson, 2016; see LICENCE in root directory
# Main script function

import sys
import ec.interface_tk
import ec.interface_cli


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if not argv or argv == ['tk']:
        ec.interface_tk.main()
    elif argv == ['cli']:
        ec.interface_cli.Interface()
    else:
        print("Invalid arguments. Need 'cli' or 'tk'.")

if __name__ == '__main__':
    main()
