import Tkinter as tk
import ttk
import threading


def close_ed(parent, edwin):
    parent.focus_set()
    edwin.destroy()

def set_cell(edwin, w, tvar):
	#global sample_dict
    value = tvar.get()
    w.item(w.focus(), values=(value,))
    t_dict = w._source_dict
    key_path=w.focus().split('///')
    for i in range(len(key_path)-2):
    	t_dict = t_dict[key_path[i+1]]
    t_dict[key_path[-1]] = value
    #print w._source_dict
    close_ed(w, edwin)

def edit_cell(e):
    w = e.widget
    if w and len(w.item(w.focus(), 'values')) > 0:
        edwin = tk.Toplevel(e.widget)
        edwin.protocol("WM_DELETE_WINDOW", lambda: close_ed(w, edwin))
        edwin.grab_set()
        edwin.overrideredirect(1)
        opt_name = w.focus()
        (x, y, width, height) = w.bbox(opt_name, 'Values')
        edwin.geometry('%dx%d+%d+%d' % (width, height, w.winfo_rootx() + x, w.winfo_rooty() + y))
        value = w.item(opt_name, 'values')[0]
        tvar = tk.StringVar()
        tvar.set(str(value))
        ed = tk.Entry(edwin, textvariable=tvar)
        if ed:
            ed.config(background='LightYellow')
            #ed.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.W, tk.E))
            ed.pack()
            ed.focus_set()
        edwin.bind('<Return>', lambda e: set_cell(edwin, w, tvar))
        edwin.bind('<Escape>', lambda e: close_ed(w, edwin))

def fill_tree(tree, parent, source_dict,separator='///'):
    for key in source_dict :
        if isinstance(source_dict[key], dict):
            tree.insert(parent, 'end', parent+separator+key, text=key)
            fill_tree(tree, parent+separator+key, source_dict[key])
        elif isinstance(source_dict[key], list):
            tree.insert(parent, 'end', parent+separator+key, text=key) # Still working on this
        else:
            if source_dict[key]==None:
                tree.insert(parent, 'end', parent+separator+key, text=key, value='None')
            else:
                tree.insert(parent, 'end', parent+separator+key, text=key, value=source_dict[key])




def create_dict_editor(source_dict):
    # Setup the root UI
    root = tk.Tk()
    root.title("JSON editor")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    # Setup Data
    # Setup the Frames
    TreeFrame = ttk.Frame(root, padding="3")
    TreeFrame.grid(row=0, column=0, sticky=tk.NSEW)
    # Setup the Tree
    tree = ttk.Treeview(TreeFrame, columns=('Values'))
    tree.column('Values', width=100, anchor='center')
    tree.heading('Values', text='Values')
    tree.bind('<Double-1>', edit_cell)
    tree.bind('<Return>', edit_cell)
    fill_tree(tree, '', source_dict)
    tree.pack(fill=tk.BOTH, expand=1)
    tree._source_dict = source_dict
    # Limit windows minimum dimensions
    root.update_idletasks()
    root.minsize(root.winfo_reqwidth(), root.winfo_reqheight())
    root.mainloop()

if __name__ == "__main__" :
	sample_dict = {
        'dict1':{
          'some par':112312,
          'second par':23.5,
          'thisrt par':'dfs',
          },
        'dict2':{
          'some par':0,
          'second par':2.5,
          'thisrt par':{'ff':'fff','gg':'ggg'},
          },
    }
	#create_dict_editor(sample_dict)
	#print sample_dict

	t = threading.Thread(target = create_dict_editor, args=(cfg,))
	t.start()