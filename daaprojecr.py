import tkinter as tk
from tkinter import ttk, messagebox
import time
import matplotlib.pyplot as plt
import networkx as nx

# -------------------------------
# DATA
# -------------------------------
posts = [
    {"id": 1, "likes": 120, "date": "2026-04-01"},
    {"id": 2, "likes": 450, "date": "2026-04-10"},
    {"id": 3, "likes": 230, "date": "2026-03-28"},
    {"id": 4, "likes": 980, "date": "2026-04-12"},
    {"id": 5, "likes": 150, "date": "2026-04-05"}
]

# -------------------------------
# SORTING
# -------------------------------
def quick_sort(arr, key, reverse=False):
    if len(arr) <= 1:
        return arr
    pivot = arr[0]
    if not reverse:
        less = [x for x in arr[1:] if x[key] <= pivot[key]]
        greater = [x for x in arr[1:] if x[key] > pivot[key]]
    else:
        less = [x for x in arr[1:] if x[key] >= pivot[key]]
        greater = [x for x in arr[1:] if x[key] < pivot[key]]
    return quick_sort(less, key, reverse) + [pivot] + quick_sort(greater, key, reverse)

def merge_sort(arr, key, reverse=False):
    if len(arr) <= 1:
        return arr
    mid = len(arr)//2
    left = merge_sort(arr[:mid], key, reverse)
    right = merge_sort(arr[mid:], key, reverse)
    return merge(left, right, key, reverse)

def merge(left, right, key, reverse):
    result = []
    while left and right:
        if (left[0][key] < right[0][key]) ^ reverse:
            result.append(left.pop(0))
        else:
            result.append(right.pop(0))
    return result + left + right

# -------------------------------
# KRUSKAL ALGORITHM
# -------------------------------
class DisjointSet:
    def __init__(self, vertices):
        self.parent = {v: v for v in vertices}

    def find(self, item):
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])
        return self.parent[item]

    def union(self, a, b):
        rootA = self.find(a)
        rootB = self.find(b)
        if rootA != rootB:
            self.parent[rootB] = rootA

def kruskal_mst(posts):
    vertices = [p["id"] for p in posts]

    edges = []
    for i in range(len(posts)):
        for j in range(i+1, len(posts)):
            weight = abs(posts[i]["likes"] - posts[j]["likes"])
            edges.append((posts[i]["id"], posts[j]["id"], weight))

    edges.sort(key=lambda x: x[2])

    ds = DisjointSet(vertices)
    mst = []
    total_cost = 0

    for u, v, w in edges:
        if ds.find(u) != ds.find(v):
            ds.union(u, v)
            mst.append((u, v, w))
            total_cost += w

    return mst, total_cost

# -------------------------------
# FUNCTIONS
# -------------------------------
def refresh_table(data):
    for row in tree.get_children():
        tree.delete(row)
    for post in data:
        tree.insert("", "end", values=(post["id"], post["likes"], post["date"]))

def sort_posts():
    key = key_var.get()
    reverse = order_var.get() == "Descending"
    algo = algo_var.get()

    start = time.time()
    if algo == "Quick Sort":
        result = quick_sort(posts.copy(), key, reverse)
    else:
        result = merge_sort(posts.copy(), key, reverse)
    end = time.time()

    refresh_table(result)
    time_label.config(text=f"Time: {end-start:.6f} sec")

def add_post():
    try:
        new_id = int(id_entry.get())
        likes = int(likes_entry.get())
        date = date_entry.get()

        posts.append({"id": new_id, "likes": likes, "date": date})
        refresh_table(posts)

        id_entry.delete(0, tk.END)
        likes_entry.delete(0, tk.END)
        date_entry.delete(0, tk.END)
    except:
        messagebox.showerror("Error", "Enter valid data!")

def delete_post():
    selected = tree.selection()
    if not selected:
        return
    item = tree.item(selected[0])["values"]
    for p in posts:
        if p["id"] == item[0]:
            posts.remove(p)
            break
    refresh_table(posts)

# -------------------------------
# GRAPH (LIKES)
# -------------------------------
def show_graph():
    ids = [p["id"] for p in posts]
    likes = [p["likes"] for p in posts]

    plt.figure()
    plt.bar(ids, likes)
    plt.xlabel("Post ID")
    plt.ylabel("Likes")
    plt.title("Post Likes Graph")
    plt.show()

# -------------------------------
# MST GRAPH (KRUSKAL)
# -------------------------------
def show_mst():
    mst, cost = kruskal_mst(posts)

    G = nx.Graph()

    for u, v, w in mst:
        G.add_edge(u, v, weight=w)

    pos = nx.spring_layout(G)

    plt.figure()
    nx.draw(G, pos, with_labels=True)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

    plt.title(f"Kruskal MST (Total Cost: {cost})")
    plt.show()

    messagebox.showinfo("MST Result", f"Total Cost = {cost}\nEdges = {mst}")

# -------------------------------
# GUI
# -------------------------------
root = tk.Tk()
root.title("Social Media Post Sorter")
root.geometry("800x600")
root.configure(bg="#f5f5f5")

tk.Label(root, text="Social Media Post Sorter",
         font=("Arial", 20, "bold"), bg="#f5f5f5").pack(pady=10)

# Controls
control_frame = tk.Frame(root, bg="#f5f5f5")
control_frame.pack(pady=5)

key_var = tk.StringVar(value="likes")
order_var = tk.StringVar(value="Ascending")
algo_var = tk.StringVar(value="Quick Sort")

ttk.Combobox(control_frame, textvariable=key_var, values=["likes", "date"], width=10).grid(row=0, column=0, padx=5)
ttk.Combobox(control_frame, textvariable=order_var, values=["Ascending", "Descending"], width=12).grid(row=0, column=1, padx=5)
ttk.Combobox(control_frame, textvariable=algo_var, values=["Quick Sort", "Merge Sort"], width=15).grid(row=0, column=2, padx=5)

tk.Button(control_frame, text="Sort", command=sort_posts, bg="blue", fg="white").grid(row=0, column=3, padx=5)

# Table
tree = ttk.Treeview(root, columns=("ID", "Likes", "Date"), show="headings", height=10)
tree.heading("ID", text="ID")
tree.heading("Likes", text="Likes")
tree.heading("Date", text="Date")
tree.pack(pady=10)

# Input Section
input_frame = tk.Frame(root, bg="#f5f5f5")
input_frame.pack(pady=10)

tk.Label(input_frame, text="ID", bg="#f5f5f5").grid(row=0, column=0)
tk.Label(input_frame, text="Likes", bg="#f5f5f5").grid(row=0, column=1)
tk.Label(input_frame, text="Date", bg="#f5f5f5").grid(row=0, column=2)

id_entry = tk.Entry(input_frame, width=10)
likes_entry = tk.Entry(input_frame, width=10)
date_entry = tk.Entry(input_frame, width=15)

id_entry.grid(row=1, column=0, padx=5)
likes_entry.grid(row=1, column=1, padx=5)
date_entry.grid(row=1, column=2, padx=5)

tk.Button(input_frame, text="Add Post", command=add_post, bg="green", fg="white").grid(row=1, column=3, padx=5)
tk.Button(input_frame, text="Delete Selected", command=delete_post, bg="red", fg="white").grid(row=1, column=4, padx=5)

# Graph Buttons
tk.Button(root, text="Show Graph 📊", command=show_graph, bg="purple", fg="white").pack(pady=5)
tk.Button(root, text="Show MST (Kruskal) 🌳", command=show_mst, bg="orange", fg="white").pack(pady=5)

# Time Label
time_label = tk.Label(root, text="", bg="#f5f5f5")
time_label.pack()

# Init
refresh_table(posts)

root.mainloop()