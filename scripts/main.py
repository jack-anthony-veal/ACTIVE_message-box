from app import App
from StateNavigator import StateNavigator

def main():

    app = App() # declare object superclass

    state_manager = StateNavigator(app)