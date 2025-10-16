from src.frontend.interface import Interface
from src.utils.end_flow import EndFlow


def main():
    flow = EndFlow()
    app = Interface(flow)
    app.mainloop()


if __name__ == "__main__":
    main()
