from Classes import DataModel, Header, Somministrazioni, Anagrafica, Regionale

# create Data Model
dm = DataModel()

# Introduzione
Header(dm)

# Somministrazioni
somm = Somministrazioni()
somm.Analisi()

# Anagrafica
ana = Anagrafica()
ana.Analisi()

# Regionale
reg = Regionale()
reg.Analisi()

