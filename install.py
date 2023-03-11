import os
import sys

def update_requirements():
    # Get the list of installed packages
    output = os.popen('pip freeze').read()

    # Write the list of packages to the requirements.txt file
    with open('requirements.txt', 'w') as f:
        f.write(output)

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
    update_requirements()