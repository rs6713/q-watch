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
movie_title_entry = tk.Entry(
  width=20,
  bg="white", fg="black"
)
movie_title_entry.pack()
movie_title = movie_title_entry.get()
search = tk.Button(
  text="Search Movie",
  width=15, height=3
)
search.pack()

#text_box.get(tk.START, tk.END)

#entry.insert(0, text)


# Run Tkinter event loop, listens for events, button clicks, blocks other code running til window closes.
window.mainloop()