import os
import sys

if __name__ == '__main__':
    if sys.argv[1] == '-u':
        for package in sys.argv[2:]:
            # Uninstall the desired package using pip
            os.system(f'pip uninstall {package}')
    else:
        for package in sys.argv[1:]:
            # Install the desired package using pip
            os.system(f'pip install {package}')

    # Update the requirements.txt file
    os.system('pip freeze > requirements.txt')