import re
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient()
db = client["cppcompsci"]
pages = db["pages"]
professors = db["professors"]
target_page = "https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml"
fields = ["Title", "Office", "Phone", "Email", "Web"]

faculty_page = pages.find_one({"url": target_page})

if faculty_page is not None:
    faculty_page = BeautifulSoup(faculty_page["html"], "html.parser")
    faculty_section = faculty_page.find("section", id="s0")
    if faculty_section is None:
        raise LookupError("Faculty section not found")
    for entry in faculty_section.find_all("div"):
        name = entry.find("h2")
        if name is None:
            continue
        else:
            name = name.text
        details = entry.find("p")
        faculty_fields = []
        for i in range(3):
            try:
                faculty_fields.append(details.text.split(fields[i] + ":")[1]
                                   .split(fields[i+1] + ":")[0].strip())
            except (AttributeError, TypeError):
                faculty_fields.append(None)
        title, office, phone, *ra = faculty_fields
        email = entry.find("a", href=re.compile("^mailto:"))
        if email is not None:
            email = email["href"].split("mailto:")[1].strip()
        website = entry.find("a", href=re.compile("^http"))
        if website is not None:
            website = website["href"]
        professors.insert_one({"name": name, "title": title,
                               "office": office, "phone": phone,
                               "email": email, "website": website})
else:
    raise LookupError("Faculty page not found")

print("Professor database compiled.")
