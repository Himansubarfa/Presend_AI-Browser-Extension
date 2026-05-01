import json, random

templates = [
    "Flat {num}, {apartment}, {area}, {city}",
    "Plot {num}, {sector}, {city}",
    "House No. {num}, {street}, {city}",
    "Door {num}, {block}, {city}",
    "{num} {street}, {area}, {city}",
    "{apartment}, {num} {street}, {city}",
    "{num}, {area}, {city} - {pincode}",
    "Wing {wing}, {apartment}, {area}, {city}",
    "Building {num}, {complex}, {city}",
    "Shop {num}, {market}, {city}",
]

apartments = ["Sunrise Apartment","Krishna Residency","Ganga Heights","Shanti Villa","Royal Palace","Silver Oak","Green Acres"]
areas = ["Koramangala","Indiranagar","Whitefield","HSR Layout","Jayanagar","Marathahalli","Begur","BTM Layout"]
cities = ["Bangalore","Mumbai","Delhi","Hyderabad","Chennai","Kolkata","Pune","Ahmedabad"]
streets = ["MG Road","Church Street","Brigade Road","Commercial Street","100 Feet Road","Outer Ring Road"]
sectors = ["Sector 21","Sector 14","Sector 7","Sector 62"]
blocks = ["A Block","B Block","C Block","D Block"]
markets = ["Main Market","Central Market","City Centre"]
complexes = ["Tech Park","Business Hub","Trade Centre"]
wings = ["A","B","C","D"]

lines = []
for _ in range(3000):
    t = random.choice(templates)
    text = t.format(
        num=random.randint(1,999),
        apartment=random.choice(apartments),
        area=random.choice(areas),
        city=random.choice(cities),
        street=random.choice(streets),
        sector=random.choice(sectors),
        block=random.choice(blocks),
        market=random.choice(markets),
        complex=random.choice(complexes),
        wing=random.choice(wings),
        pincode=random.choice(["560001","560002","560003","560004","560005"]),
    )
    lines.append({"text": f"Address: {text}.", "entities": []})

with open("data/more_addresses.jsonl","w") as f:
    for l in lines:
        f.write(json.dumps(l)+"\n")
print("Done")