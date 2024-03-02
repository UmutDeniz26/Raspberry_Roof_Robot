import gps

def main():
    # Connect to the local gpsd service (default port)
    session = gps.gps("localhost", "2947")
    session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

    try:
        while True:
            report = session.next()
            if report['class'] == 'TPV':
                if hasattr(report, 'lat') and hasattr(report, 'lon'):
                    latitude = getattr(report, 'lat', "n/a")
                    longitude = getattr(report, 'lon', "n/a")
                    print("Latitude: {}, Longitude: {}".format(latitude, longitude))
            elif report['class'] == 'SKY':
                if hasattr(report, 'satellites'):
                    satellites = getattr(report, 'satellites', "n/a")
                    print("Satellites in use: {}".format(satellites))

    except KeyboardInterrupt:
        print("Exiting")
    except StopIteration:
        session = None
        print("GPSD has terminated")

if __name__ == '__main__':
    main()
