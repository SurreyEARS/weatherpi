import metoffer
api_key = '7fe18ea6-ca0d-4952-b166-aa0a0ae19ffb'
M = metoffer.MetOffer(api_key)
x = M.nearest_loc_forecast(51.215340, -0.602149, metoffer.THREE_HOURLY)
y = metoffer.parse_val(x)
z = y.data[0]
print(z)

