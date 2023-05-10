import ***REMOVED***.config as c

from ***REMOVED***.***REMOVED***Handler import parse***REMOVED***ERs
from ***REMOVED***.pdu_encoder import create_pdu_encoder


def ***REMOVED***():
    required_event_reports = c.req_ers

    unisim_event_reports = parse***REMOVED***ERs()

    create_pdu_encoder(required_event_reports, unisim_event_reports)
