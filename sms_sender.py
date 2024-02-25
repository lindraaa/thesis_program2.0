import serial
import time

def send_sms():
    # Define variables
    serial_port = '/dev/ttyS0'
    recipient_number = "+639771136735"
    message = "Someone is attempting to unlock your car"

    # Configure the serial port
    ser = serial.Serial(serial_port, 9600, timeout=1)

    try:
        # Check if the serial port is open
        if not ser.isOpen():
            ser.open()

        # Wait for the modem to initialize
        time.sleep(2)

        # Set the SMS center number (replace with your SMS center number)
        ser.write(b'AT+CSCA="+639694738954"\r\n')
        response = ser.read(100)
        print("SENDING")

        # Send SMS command
        ser.write('AT+CMGS="{}"\r\n'.format(recipient_number).encode())
        response = ser.read(100)
        print("SENDING")

        # Send the SMS message content
        ser.write('{}\x1A\r\n'.format(message).encode())
        response = ser.read(100)
        print("Message Sent")

    except serial.SerialException as e:
        print("Serial port error:", e)
    finally:
        # Close the serial port
        ser.close()

# Example usage
#if __name__ == "__main__":
#    send_sms()
