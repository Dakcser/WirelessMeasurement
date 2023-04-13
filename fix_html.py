from bs4 import BeautifulSoup


def move_imageOverlay_to_back():
    """
    Modifies "index.html" by adding a CSS rule to set the z-index of `.leaflet-image-layer`
    to -1, pushing the image overlay behind other layers in a leaflet map. The function
    reads and parses the HTML, updates the `<style>` element, and writes the changes
    back to the file.
    """
    
    # Read the HTML file into a string
    with open('index.html', 'r') as file:
        html = file.read()

    # Parse the HTML string using BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Find the <style> element containing the target line of code
    style_element = soup.find('style', string=lambda string: '.leaflet-container { font-size: 1rem; }' in string)

    # Extract the contents of the <style> element as a string
    style_string = str(style_element.string)

    # Modify the string to include the new line of code
    modified_style_string = style_string + "</style> \n\n <style>.leaflet-image-layer{z-index:-1 !important}</style>\n"

    # Replace the original <style> element with the modified string
    style_element.string.replace_with(modified_style_string)

    # Write the modified HTML string back to the file
    with open('index.html', 'w') as file:
        file.write(str(soup))