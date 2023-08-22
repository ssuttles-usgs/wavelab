import tkinter as tk

class MessageDialog(tk.Toplevel):
    """ A template for nice dialog boxes. """

    def __init__(self, parent, message="", title="", buttons=1, wait=True):
        tk.Toplevel.__init__(self, parent)
        body = tk.Frame(self)
        self.title(title)
        self.boolean = None
        self.parent = parent
        self.transient(parent)
        tk.Label(body, text=message).pack()
        if buttons == 1:
            b = tk.Button(body, text="OK", command=self.destroy)
            b.pack(pady=5)
        elif buttons == 2:
            buttonframe = tk.Frame(body, padding="3 3 5 5")
            def event(boolean):
                self.boolean = boolean
                self.destroy()
            b1 = tk.Button(buttonframe, text='YES',
                           command=lambda: event(True))
            b1.grid(row=0, column=0)
            b2 = tk.Button(buttonframe, text='NO',
                           command=lambda: event(False))
            b2.grid(row=0, column=1)
            buttonframe.pack()
        body.pack()
        self.grab_set()
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))
        if wait:
            self.wait_window(self)

