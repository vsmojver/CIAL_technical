import functions
import sys

url = sys.argv[1]

soup = functions.make_soup(url)
phone_numbers = str(functions.get_numbers(soup))
logo = functions.find_logo(soup)


sys.stdout.write(phone_numbers+"\n")
if logo:
    logo_url = functions.return_logo_url(logo, url)
    sys.stdout.write(logo_url+"\n")
else:
    logo_url = None
    sys.stdout.write('None\n')
