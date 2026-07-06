from edge_gateway.runtime.application import Application
from edge_gateway.config.config_loader import load_config


def main():

    config = load_config()

    app = Application(config)
    app.build()
    app.run()


if __name__ == "__main__":
    main()