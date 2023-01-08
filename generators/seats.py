import random
import string

def generate(locations):

    current_id = 0
    seats = {}

    for location_id, location in locations.items():
        numbering_style = random.randint(1,3)
        for i in range(int(location["capacity"])):
            number = 0
            seat_type = None
            if numbering_style == 1:
                # simple numbering
                number = i
            elif numbering_style == 2:
                # using letters
                number = random.choice(string.ascii_uppercase) + str(i)
            elif numbering_style == 3:
                # including seat type
                types = (("FRO", 9),  # front row
                         ("BALC", 5), # balcony
                         ("REAR", 2), # rear
                         ("BOX", 10), # box
                         ("MID", 5 )) # center
                         
                t = random.choice(types)
                number = "{}-{}".format(t[0],i)
                seat_type = t[1]
                
            seat = {"number": number,
                    "location_id": location_id,
                    "type": seat_type if seat_type else random.randint(1, 10)}
            seats[current_id] = seat
            current_id += 1

    return seats
