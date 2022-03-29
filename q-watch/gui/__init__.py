import tkinter as tk


window = tk.Tk(
  background="#f2c7ee"
)

# Label widget
welcome = tk.Label(
  text="Add Movie",
  width="10, height=2
)
welcome.pack()

# Movie Title
movie_title = tk.Entry(
  width=20,
  bg="white", fg="black"
)
movie_title.pack()
search = tk.Button(
  text="Search Movie",
  width=15, height=3
)
search.pack()


# Run Tkinter event loop, listens for events, button clicks, blocks other code running til window closes.
window.mainloop()