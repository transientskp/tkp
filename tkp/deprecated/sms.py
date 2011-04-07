#
# LOFAR Transients Key Project
#
"""
Facility for sending SMS (text) messages.

Quickly hacked together for demonstration purposes; this is not a solid
implementation.
"""

import socket, logging

# Essential parameters for sending.
# (Leading __ marks as private, at least for epydoc; these shouldn't really be
# needed outside this module)
__host       = 'xml1.aspsms.com'
__port       = 5061
__userkey    = "KED9X1UHAU5H"
__password   = "transients"
__originator = "LOFAR"

def send_sms(recipient, text):
    """
    Send an SMS message.

    A message is sent to a single receiver; the originator is "LOFAR". No
    worthwhile error checking is done, and nothing returned.

    This code based on U{http://www.aspsms.com/examples/python/}.

    @type  recipient: string
    @param recipient: Receiving phone number.
    @type  text:      string
    @param text:      Message to send.
    """

    CONTENT = """<?xml version="1.0" encoding="ISO-8859-1"?>
      <aspsms>
       <Userkey>"""+str(__userkey)+"""</Userkey>
        <Password>"""+str(__password)+"""</Password>
        <Originator>"""+ str(__originator) +"""</Originator>
        <Recipient>
        <PhoneNumber>"""+ str(recipient) +"""</PhoneNumber>
        </Recipient>
        <MessageData>"""+ str(text) +"""</MessageData>
        <Action>SendTextSMS</Action>
        </aspsms>"""

    length = len(CONTENT)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((__host, __port))
    s.send("POST /xmlsvr.asp HTTP/1.0\r\n")
    s.send("Content-Type: text/xml\r\n")
    s.send("Content-Length: "+str(length)+"\r\n\r\n")
    s.send(CONTENT)
    datarecv = s.recv(1024)
    logging.debug("Reply Received: "+ str(datarecv))
    s.close()

