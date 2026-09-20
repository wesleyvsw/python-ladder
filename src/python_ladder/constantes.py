NO_BARRAMENTO = 0  # nó 0 = barramento energizado (powerrail)
VERSAO_TIA = "V17"

# (tipo, subtipo) -> nome do Part no XML do TIA Portal
PARTS_TIA = {
    "contato": {"1": "Contact", "p": "Pcontact", "n": "NContact", "f": "Contact"},
    "bobina": {"1": "Coil", "c": "Coil", "r": "RCoil", "s": "SCoil"},
}
