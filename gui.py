import PySimpleGUI as sg
from reportlab.pdfgen.canvas import Canvas
from reportlab_qrcode import QRCodeImage
import time
import re


from app import App
import filters


GUI_USER = "mmckinlay0@vinaora.com"
UPLAT = 38.289365
UPLONG = 21.784715

search_events_column = [
        [
            sg.Text("Search"),
            sg.In(size=(25, 1), enable_events=True, key="-SEARCH-"),
            sg.Button("Search", bind_return_key=True)
        ],
        [
            sg.Text("Filters", font="Arial 15 bold")
        ],
        [
            sg.Text("Type"),
            sg.Combo(["All", "Theater", "Concert"], size=(12, 1), enable_events=True, default_value="All", readonly=True, key="-TYPE-")
        ],
        [
            sg.Checkbox("Show only available", default=True, enable_events=True, key="-AVAILABLE-")
        ],
        [
            sg.Text("Distance from UP less than:"),
            sg.In(size=(5, 1), enable_events=True, key="-DISTANCE-")
        ],
        [
            sg.Text("Date before:"),
            sg.Input("", key="-BEFORE DATE-", size=(19, 1), readonly=True, enable_events=True),
        ],
        [
            sg.CalendarButton("Choose Date", target='-BEFORE DATE-'),
            sg.Button("Clear Date", enable_events=True)
        ],
        [
            sg.Listbox(
                    values=[], metadata=[], enable_events=True, size=(40, 20), key="-EVENT LIST-"
                )
        ]
]

event_data_and_happenings = [
        [
            sg.Text("Event", key="-EVENT NAME-")
        ],
        [
            sg.Text("Select an event to continue", size=(60, None), key="-EVENT DESCRIPTION-")
        ],
        [
            sg.Listbox(
                    values=[], enable_events=True, size=(60, 25), key="-HAPPENING LIST-"
                )
        ],
        [
            sg.Button("Book Now", disabled=True)
        ]
]

search_layout = [

    [

        sg.Column(search_events_column),

        sg.VSeperator(),

        sg.Column(event_data_and_happenings),

    ]

]


def create_row(num):
    return [sg.Col([[
        sg.Text(f"[Ticket #{num+1}]  Name:"),
        sg.Input(size=(30, 1), key=("-NAME-", num), enable_events=True),
    ]], visible=False, key=('-TICKET ROW-', num))]

book_layout = [[
    sg.Column([
        [
            sg.Button(button_text="←", size=(1, 1), font="Arial 15 bold"),
        ],
        [
            sg.Text("Book: EVENT_NAME", font="Arial 18 bold", key="-BOOKING TITLE-")
        ],
        [
            sg.Text("", size=(47, None), font="Arial 13", key="-BOOKING DESCRIPTION-")
        ],
        [
            sg.Text("Number of tickets:", font="Arial 13"),
            sg.Input(default_text = "1", size=(1, 1), enable_events=True, key="-TICKETS NO-", font="Arial 15")
        ],
        [
            sg.Column([create_row(i) for i in range(6)], size=(500, 200), key="-NEW TICKETS-")
        ],
        [
            sg.Push(),
            sg.Button("BOOK", size=(20, 4), disabled=True),
            sg.Push()
        ]
    ], justification='center', size=(500, 600))
]]


layout = [[sg.Column(search_layout, key="-COL1-"), sg.Column(book_layout, visible=False, key="-COL2-")]]


def update_event_list(window, values, app):
    all_filters = []

    search_text = values["-SEARCH-"]
    if search_text:
        all_filters.append(filters.FieldContains("Event", "name", values["-SEARCH-"]))

    cat = values["-TYPE-"]
    if cat != "All":
        all_filters.append(filters.EventCategory(cat))

    events = app.get_table_fields("Event", ["name", "id"], all_filters)
    event_names = [e[0] for e in events]
    event_ids = [e[1] for e in events]
    window["-EVENT LIST-"].update(event_names)
    window["-EVENT LIST-"].metadata = event_ids


def update_happening_list(window, values, app):
    if not window.Element("-EVENT LIST-").get_indexes():
        return

    event_name = values["-EVENT LIST-"][0]
    window["-EVENT NAME-"].update(event_name)

    idx = window.Element("-EVENT LIST-").get_indexes()[0]
    event_id = window.Element("-EVENT LIST-").metadata[idx]

    event_info = app.get_table_fields("Event", ["description", "category"], [filters.Filter(["Event"], "id = ?")], True, event_id)[0]

    window["-EVENT DESCRIPTION-"].update(f"({event_info[1]})\n{event_info[0]}")

    selected_filters = []
    if values["-AVAILABLE-"]:
        selected_filters.append(filters.HappeningAvailable())

    dist = values["-DISTANCE-"]
    if dist:
        selected_filters.append(filters.HappeningDistance(UPLAT, UPLONG, dist))

    # only show happenings in the future
    selected_filters.append(filters.HappeningTime("now", after=True))

    date = window["-BEFORE DATE-"].get()
    if date:
        selected_filters.append(filters.HappeningTime(date))

    result = app.get_happening_descriptions(selected_filters + [filters.HappeningByEvent(event_id)])
    ids = [r[0] for r in result]
    details = [r[1] for r in result]

    window["-HAPPENING LIST-"].update(details)
    window["-HAPPENING LIST-"].metadata = ids


def update_book_button_status(window, values):
    selected = values["-HAPPENING LIST-"]
    pattern = r"([0-9\- :]*) @ (.*) \((\d+) available seat\(s\)\)"
    if selected:
        match = re.search(pattern, selected[0])
        available_seats = int(match.group(3))
        if available_seats:
            window["Book Now"].update(disabled=False)

            idx = window.Element("-HAPPENING LIST-").get_indexes()[0]
            happening_id = window.Element("-HAPPENING LIST-").metadata[idx]
            info = {"id": happening_id,
                    "datetime": match.group(1),
                    "location_name": match.group(2),
                    "available_seats": available_seats
                   }

            window["Book Now"].metadata = info
            return
    window["Book Now"].update(disabled=True)


def goto_book_page(window, values):
    window["-COL1-"].update(visible=False)
    window["-COL2-"].update(visible=True)

    event_name = values["-EVENT LIST-"][0]
    window["-BOOKING TITLE-"].update(event_name)

    window["-TICKETS NO-"].update("1")

    happening_info = window["Book Now"].metadata

    desc = window['-EVENT DESCRIPTION-'].get() + '\n\n' + \
            "Time: " + happening_info['datetime'] + '\n' + \
            "Place: " + happening_info['location_name'] + '\n\n' + \
            "Available seat(s): " + str(happening_info['available_seats'])

    window["-BOOKING DESCRIPTION-"].update(desc)

def goto_search_page(window, values):
    window["-COL1-"].update(visible=True)
    window["-COL2-"].update(visible=False)
    update_book_button_status(window, values)

def check_ticket_no_value(window, values):
    tickets_no = values['-TICKETS NO-']
    if tickets_no and tickets_no.isnumeric():
        i = int(tickets_no)
        if i > 0 and i < 7:
            return

    window['-TICKETS NO-'].update('1')
    values['-TICKETS NO-'] = '1'

def get_ticket_rows_data(window, values):
    tickets = []
    for i in range(6):
        if window[('-TICKET ROW-', i)].visible:
            name = values[('-NAME-', i)]
            if name:
                tickets.append(name)
    return tickets

def update_ticket_rows(window, values):
    number_of_rows = int(values['-TICKETS NO-'])
    for i in range(number_of_rows):
        window[('-TICKET ROW-', i)].update(visible = True)
    for i in range(number_of_rows, 6):
        window[('-TICKET ROW-', i)].update(visible = False)


def update_final_button_status(window, values):
    tickets = get_ticket_rows_data(window, values)
    if len(tickets) == int(values['-TICKETS NO-']):
        window['BOOK'].update(disabled=False)
    else:
        window['BOOK'].update(disabled=True)

def generate_ticket_pdf(ticket_id):
    ticket_data = app.get_ticket_info(ticket_id)
    c = Canvas(f"ticket-{ticket_id}.pdf")
    c.setPageSize((500, 170))
    img_file = "images/up_ece_logo.png"

    qr = QRCodeImage(ticket_data['barcode'], size=80)
    qr.drawOn(c, 5, 12)

    c.drawImage(img_file, 13, 48, width=120, preserveAspectRatio=True, mask='auto')

    c.drawString(100, 78, f"Name: {ticket_data['name']}")
    c.drawString(100, 58, f"Event: {ticket_data['event_name']}")
    c.drawString(100, 38, f"Date: {ticket_data['datetime']}")
    c.drawString(100, 18, f"Seat: {ticket_data['seat']}")


    c.showPage()
    c.save()

def book_tickets(window, values, app):
    happening_id = window['Book Now'].metadata['id']
    names = get_ticket_rows_data(window, values)
    ticket_ids = app.book(GUI_USER, happening_id, names)
    for ti in ticket_ids:
        generate_ticket_pdf(ti)
    sg.PopupOK(f"Successfully booked {len(ticket_ids)} ticket(s)!", title="Success")


# Connect to app
app = App("database.db")

# Create the window
window = sg.Window("Database Demo", layout)

event, values = window.read(timeout=1)
update_event_list(window, values, app)

# Create an event loop
while True:
    event, values = window.read()
    # End program if user closes window or
    # presses the OK button
    if event == "OK" or event == sg.WIN_CLOSED:
        break
    if event == "Clear Date":
        window['-BEFORE DATE-'].update('')
    if event in ["Search", "-TYPE-"]:
        update_event_list(window, values, app)
    elif event in ["Clear Date", "-EVENT LIST-", "-AVAILABLE-", "-DISTANCE-", "-BEFORE DATE-"]:
        # a new event was selected or filters where updated
        update_happening_list(window, values, app)
        values['-HAPPENING LIST-'] = []
        update_book_button_status(window, values)
    elif event == "-HAPPENING LIST-":
        update_book_button_status(window, values)
    elif event == "Book Now":
        goto_book_page(window, values)
        update_ticket_rows(window, values)
    elif event == "-TICKETS NO-":
        check_ticket_no_value(window, values)
        update_ticket_rows(window, values)
        update_final_button_status(window, values)
    elif event in [("-NAME-", i) for i in range(6)]:
        update_final_button_status(window, values)
    elif event == "BOOK":
        book_tickets(window, values, app)
        goto_search_page(window, values)
    elif event == "←":
        goto_search_page(window, values)

window.close()
