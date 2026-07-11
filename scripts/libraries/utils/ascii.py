import time


def boxed_line(text):
    text = str(text)[:14]
    return "|" + text.center(14) + "|"


def make_loading_frame(title, face, heart_line):
    return [
        "+--------------+",
        boxed_line(title),
        "|   /\\_/\\      |",
        boxed_line(face),
        "|" + str(heart_line)[:14].ljust(14) + "|",
        "+--------------+",
    ]


CUTE_LOADING_FRAMES = [
    make_loading_frame("loading",    "( o.o )", "<3"),
    make_loading_frame("loading.",   "( o.o )", " <3"),
    make_loading_frame("loading..",  "( -.- )", "  <3"),
    make_loading_frame("loading...", "( -.- )", "   <3"),
    make_loading_frame("loading",    "( ^.^ )", "    <3"),
    make_loading_frame("loading.",   "( ^.^ )", "     <3"),
    make_loading_frame("loading..",  "( o.o )", "      <3"),
    make_loading_frame("loading...", "( o.o )", "       <3"),
    make_loading_frame("loading",    "( ^.^ )", "      <3"),
    make_loading_frame("loading.",   "( ^.^ )", "     <3"),
    make_loading_frame("loading..",  "( -.- )", "    <3"),
    make_loading_frame("loading...", "( o.o )", "   <3"),
]


CUTE_ERROR_BOX = [
    "+--------------+",
    "|  tiny error  |",
    "|   /\\_/\\      |",
    "|  ( ;.; )     |",
    "| press back <3|",
    "+--------------+",
]


CUTE_WIFI_ERROR_BOX = [
    "+--------------+",
    "|  no wifi :(  |",
    "|   /\\_/\\      |",
    "|  ( >.< )     |",
    "| try again <3 |",
    "+--------------+",
]


CUTE_API_ERROR_BOX = [
    "+--------------+",
    "| api sleepy   |",
    "|   /\\_/\\ zZ   |",
    "|  ( -.- )     |",
    "| back pls <3  |",
    "+--------------+",
]
