"""TfL transport zone → London postcode district mapping.

Each postcode district is assigned to its primary zone. Many districts straddle
zone boundaries; they are placed in the zone covering the majority of their area.

Usage:
    from flathunter.crawler.url_builders.london_zones import expand_zones

    areas = expand_zones([1, 2])  # returns list of postcode district strings
"""

from typing import List

# Postcode districts keyed by TfL zone (primary zone assignment).
# Zones 1–5 cover the area served by the London Underground / Overground.
TFL_ZONES: dict = {
    1: [
        # City of London / East Central
        "EC1", "EC2", "EC3", "EC4",
        # West Central (Bloomsbury, Covent Garden, Strand)
        "WC1", "WC2",
        # West End (Mayfair, Soho, Oxford Street, Marylebone)
        "W1",
        # South West / Westminster (Victoria, Pimlico, Belgravia)
        "SW1",
        # South East (Borough, Waterloo, Bermondsey — mainly Z1)
        "SE1",
        # North (Angel / Islington — partly Z1)
        "N1",
        # East (Aldgate, Whitechapel — partly Z1)
        "E1",
    ],
    2: [
        # North West
        "NW1",   # Camden Town, Euston, Marylebone
        "NW3",   # Hampstead, Swiss Cottage
        "NW5",   # Kentish Town
        "NW6",   # Kilburn, West Hampstead
        "NW8",   # St John's Wood
        # West
        "W2",    # Paddington, Bayswater
        "W6",    # Hammersmith
        "W9",    # Maida Vale
        "W10",   # Ladbroke Grove
        "W11",   # Notting Hill
        "W12",   # Shepherd's Bush
        "W14",   # West Kensington
        # South West
        "SW3",   # Chelsea
        "SW5",   # Earl's Court
        "SW6",   # Fulham
        "SW7",   # South Kensington
        "SW8",   # South Lambeth, Battersea
        "SW9",   # Stockwell, Brixton
        "SW10",  # World's End
        "SW11",  # Battersea, Clapham Junction
        # South East
        "SE5",   # Camberwell
        "SE11",  # Kennington, Vauxhall
        "SE15",  # Peckham
        "SE17",  # Elephant & Castle, Walworth
        # East
        "E2",    # Bethnal Green, Shoreditch
        "E3",    # Bow
        "E8",    # Hackney, Dalston
        "E9",    # Homerton
        "E14",   # Canary Wharf, Poplar
        # North
        "N4",    # Finsbury Park
        "N5",    # Highbury
        "N7",    # Holloway
        "N16",   # Stoke Newington
        "N19",   # Upper Holloway
    ],
    3: [
        # North West
        "NW2",   # Cricklewood
        "NW4",   # Hendon
        "NW10",  # Harlesden
        # West
        "W3",    # Acton
        "W4",    # Chiswick
        "W5",    # Ealing
        "W7",    # Hanwell
        "W13",   # West Ealing
        # South West
        "SW12",  # Balham
        "SW14",  # East Sheen
        "SW15",  # Putney
        "SW16",  # Streatham
        "SW17",  # Tooting
        "SW18",  # Wandsworth
        "SW19",  # Wimbledon
        "SW20",  # West Wimbledon
        # South East
        "SE4",   # Brockley
        "SE6",   # Catford
        "SE8",   # Deptford
        "SE10",  # Greenwich
        "SE12",  # Lee
        "SE13",  # Lewisham
        "SE14",  # New Cross
        "SE18",  # Woolwich
        "SE22",  # East Dulwich
        "SE23",  # Forest Hill
        "SE24",  # Herne Hill
        "SE25",  # South Norwood
        "SE26",  # Sydenham
        # East
        "E5",    # Clapton
        "E10",   # Leyton
        "E11",   # Leytonstone
        "E12",   # Manor Park
        "E13",   # Plaistow
        "E15",   # Stratford
        "E17",   # Walthamstow
        # North
        "N8",    # Hornsey, Crouch End
        "N11",   # New Southgate
        "N13",   # Palmers Green
        "N17",   # Tottenham
        "N22",   # Wood Green
    ],
    4: [
        # North West / Harrow
        "HA0", "HA1", "HA2", "HA3",
        # West / Southall / Hayes
        "UB1", "UB2", "UB3", "UB4",
        # South West / Twickenham / Richmond
        "TW1", "TW2", "TW3", "TW4", "TW7", "TW8", "TW9", "TW10", "TW11", "TW12",
        # South / Sutton / Morden
        "SM1", "SM2", "SM3", "SM4",
        # South / Croydon
        "CR0", "CR4",
        # South East / Bromley
        "BR1", "BR2", "BR3",
        # South East
        "SE2", "SE9", "SE16", "SE19", "SE20", "SE21", "SE27",
        # East
        "E4", "E6", "E7", "E16", "E18",
        # North
        "N9", "N12", "N14", "N15", "N18", "N20", "N21",
    ],
    5: [
        # North West / outer Harrow
        "HA4", "HA5", "HA6", "HA7", "HA8", "HA9",
        # West / outer Uxbridge
        "UB5", "UB6", "UB7", "UB8", "UB9", "UB10",
        # South West / outer Heathrow
        "TW5", "TW6", "TW13", "TW14", "TW15", "TW16",
        # South / Kingston / Surbiton
        "KT1", "KT2", "KT3", "KT4", "KT5", "KT6",
        # South / outer Sutton
        "SM5", "SM6", "SM7",
        # South / outer Croydon
        "CR2", "CR5", "CR7", "CR8",
        # South East / outer Bromley
        "BR4", "BR5", "BR6",
        # East / Ilford / Barking
        "IG1", "IG2", "IG3", "IG4", "IG5",
        "RM1", "RM2", "RM6", "RM7", "RM8", "RM9", "RM10",
        # North / Enfield
        "EN1", "EN2", "EN3", "EN4",
    ],
}


def expand_zones(zones: List[int]) -> List[str]:
    """Return a deduplicated list of postcode districts for the given TfL zone numbers."""
    seen = set()
    result = []
    for zone in zones:
        for district in TFL_ZONES.get(zone, []):
            if district not in seen:
                seen.add(district)
                result.append(district)
    return result
