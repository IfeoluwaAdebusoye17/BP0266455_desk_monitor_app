import time
import requests
import wmi

BACKEND_API_URL = 'http://127.0.0.1:5000/desks'
DOCKING_STATION_ID = 1  # Replace with actual docking station id
EMPLOYEE_ID = 1  # Replace with actual employee ID

# Initialize the WMI interface
c = wmi.WMI()

def notify_backend(docking_station_id, employee_id, occupied=True):
    url = f'{BACKEND_API_URL}/{docking_station_id}'
    data = {'employee_id': employee_id} if occupied else {'employee_id': None}  

    try:
        response = requests.put(url, json=data)
        if response.status_code == 200:
            status = 'updated successfully' if occupied else 'marked as unoccupied'
            print(f'Desk status {status}.')
        else:
            print('Failed to update desk status:', response.status_code)
    except Exception as e:
        print('Error connecting to the server:', e)

def monitor_docking_station():
    print('Listening for hardware changes...')
    docking_station_connected = False  # Track if the docking station is connected

    while True:
        try:
            # Poll for hardware changes
            connected_now = False  # To track current connection status
            for device in c.Win32_USBControllerDevice():
                device_name = device.Dependent.Caption
                if 'Generic USB Hub' in device_name:
                    print(f'Docking station detected: {device_name}')
                    connected_now = True
                    if not docking_station_connected:
                        notify_backend(DOCKING_STATION_ID, EMPLOYEE_ID, occupied=True)
                        docking_station_connected = True  # Update state to connected
                    break  # Exit loop if found

            # If not connected, check if we need to notify about disconnection
            if not connected_now and docking_station_connected:
                print('Docking station disconnected.')
                notify_backend(DOCKING_STATION_ID, EMPLOYEE_ID, occupied=False)
                docking_station_connected = False  # Update state to disconnected

            time.sleep(10)  # Poll every 10 seconds

        except Exception as e:
            print('An error occurred:', e)

if __name__ == '__main__':
    monitor_docking_station()
