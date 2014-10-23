import os
from iwantaserver import app
app.run(debug=os.getenv("DEBUG", False))
