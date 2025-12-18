import tkinter as tk
from tkinter import ttk, messagebox
import json
import urllib.request
import urllib.parse

# =================================================================================
# CLASE 1: MISIÓN
# =================================================================================
class Mision:
    def _init_(self, titulo, rango, nivel_req, fuerza_req, oro, monstruo):
        self.titulo = titulo
        self.rango = rango
        self.nivel_req = nivel_req
        self.fuerza_req = fuerza_req
        self.oro = oro
        self.objetivo = monstruo
        self.asignada_a = None

    def get_info_tablero(self):
        estado = "DISPONIBLE" if self.asignada_a is None else f"EN CURSO ({self.asignada_a})"
        return (self.rango, self.titulo, f"Nvl {self.nivel_req} / Fue {self.fuerza_req}", f"{self.oro} Oro", estado)

    def to_dict(self):
        return {
            "titulo": self.titulo, "rango": self.rango, 
            "nivel_req": self.nivel_req, "fuerza_req": self.fuerza_req,
            "oro": self.oro, "objetivo": self.objetivo, "asignada_a": self.asignada_a
        }

# =================================================================================
# CLASE 2: AVENTURERO
# =================================================================================
class Aventurero:
    def _init_(self, nombre, clase, raza, fuerza, magia, equipo):
        self.nombre = nombre
        self.clase = clase
        self.raza = raza
        self.fuerza = fuerza
        self.magia = magia
        self.equipo = equipo
        
        self.nivel = 1
        self.xp = 0
        self.xp_next = 100
        self.estado = "EN LA TABERNA" 
        self.oro_acumulado = 0

    def puede_realizar_mision(self, mision):
        if self.estado != "EN LA TABERNA":
            return False, "Ocupado en otra misión."
        if self.nivel < mision.nivel_req:
            return False, f"Nivel bajo. Requiere Nvl {mision.nivel_req}."
        if self.fuerza < mision.fuerza_req:
            return False, f"Muy debil. Requiere Fuerza {mision.fuerza_req}."
        return True, "Apto"

    def completar_mision(self, xp_ganada, oro_ganado):
        self.estado = "EN LA TABERNA"
        self.oro_acumulado += oro_ganado
        self.xp += xp_ganada
        msg = ""
        while self.xp >= self.xp_next:
            self.xp -= self.xp_next
            self.nivel += 1
            self.fuerza += 2
            self.magia += 2
            self.xp_next = int(self.xp_next * 1.5)
            msg += f"\n✨ ¡LEVEL UP! {self.nombre} sube a Nvl {self.nivel}."
        return msg

    def to_dict(self):
        return {
            "nombre": self.nombre, "clase": self.clase, "raza": self.raza,
            "fuerza": self.fuerza, "magia": self.magia, "equipo": self.equipo,
            "nivel": self.nivel, "xp": self.xp, "xp_next": self.xp_next,
            "estado": self.estado, "oro_acumulado": self.oro_acumulado
        }

# =================================================================================
# CLASE 3: GREMIO MANAGER
# =================================================================================
class GremioManager:
    def _init_(self, nombre):
        self.nombre = nombre
        self.aventureros = []
        self.misiones = []
        self.cofre = 1000

    def registrar_heroe(self, nombre, clase, raza, fue, mag, equip):
        if self.buscar_heroe(nombre): return False
        nuevo = Aventurero(nombre, clase, raza, fue, mag, equip)
        self.aventureros.append(nuevo)
        return True

    def editar_heroe(self, nombre_original, n_equipo, n_fuerza, n_magia):
        h = self.buscar_heroe(nombre_original)
        if h:
            h.equipo = n_equipo
            h.fuerza = int(n_fuerza)
            h.magia = int(n_magia)
            return True
        return False

    def publicar_mision(self, titulo, rango, nvl, fue_req, oro, monstruo):
        self.misiones.append(Mision(titulo, rango, nvl, fue_req, oro, monstruo))

    def buscar_heroe(self, nombre):
        for h in self.aventureros:
            if h.nombre == nombre: return h
        return None

    def buscar_mision(self, titulo):
        for m in self.misiones:
            if m.titulo == titulo: return m
        return None

    def asignar_mision(self, nombre_h, titulo_m):
        h = self.buscar_heroe(nombre_h)
        m = self.buscar_mision(titulo_m)
        if not h or not m: return "Datos no encontrados."
        if m.asignada_a: return "Misión ya ocupada."
        
        apto, msg = h.puede_realizar_mision(m)
        if not apto: return f"RECHAZADO: {msg}"

        m.asignada_a = h.nombre
        h.estado = "EN AVENTURA"
        return f"✅ CONTRATO: {h.nombre} partió a '{m.titulo}'."

    def reportar_exito(self, titulo_m):
        m = self.buscar_mision(titulo_m)
        if not m or not m.asignada_a: return "Error: Misión no activa."
        h = self.buscar_heroe(m.asignada_a)
        
        xp = m.oro * 2
        lvl_msg = h.completar_mision(xp, m.oro)
        tax = int(m.oro * 0.15)
        self.cofre += tax
        pago = m.oro - tax
        self.misiones.remove(m)
        return f"Misión Cumplida. {h.nombre} gana {pago} oro (Gremio +{tax}).{lvl_msg}"

    def guardar(self):
        data = {
            "cofre": self.cofre,
            "heroes": [h.to_dict() for h in self.aventureros],
            "misiones": [m.to_dict() for m in self.misiones]
        }
        try:
            with open("datos_gremio_v3.json", "w") as f: json.dump(data, f, indent=4)
            return "Datos guardados."
        except Exception as e: return f"Error: {e}"

    def cargar(self):
        try:
            with open("datos_gremio_v3.json", "r") as f: data = json.load(f)
            self.cofre = data["cofre"]
            self.aventureros = []
            for d in data["heroes"]:
                h = Aventurero(d["nombre"], d["clase"], d["raza"], d["fuerza"], d["magia"], d["equipo"])
                h.nivel = d["nivel"]
                h.xp = d["xp"]
                h.xp_next = d["xp_next"]
                h.estado = d["estado"]
                h.oro_acumulado = d["oro_acumulado"]
                self.aventureros.append(h)
            self.misiones = []
            for d in data["misiones"]:
                fue = d.get("fuerza_req", 0) 
                m = Mision(d["titulo"], d["rango"], d["nivel_req"], fue, d["oro"], d["objetivo"])
                m.asignada_a = d["asignada_a"]
                self.misiones.append(m)
            return "Datos cargados."
        except: return "No hay datos previos."

    def consulta_api(self, monster):
        url = f"https://www.dnd5eapi.co/api/monsters/?name={urllib.parse.quote(monster.lower())}"
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})) as r:
                d = json.loads(r.read().decode())
            if not d['count']: return "Monstruo no encontrado."
            u2 = f"https://www.dnd5eapi.co{d['results'][0]['url']}"
            with urllib.request.urlopen(urllib.request.Request(u2, headers={'User-Agent': 'Mozilla/5.0'})) as r2:
                det = json.loads(r2.read().decode())
            return (f"🐉 {det.get('name')}\nTipo: {det.get('type')}\nHP: {det.get('hit_points')}\nAC: {det.get('armor_class',[{}])[0].get('value')}")
        except Exception as e: return f"Error API: {e}"

# =================================================================================
# INTERFAZ GRÁFICA (GUI)
# =================================================================================
class GuildGUI:
    def _init_(self, mgr):
        self.mgr = mgr
        self.root = tk.Tk()
        self.root.title("RPG GUILD MASTER PRO - ESHMALUGULS")
        self.root.geometry("1100x700")
        self.root.configure(bg="#2c3e50")
        self.estilos()
        self.crear_widgets()
        self.actualizar_tablas()
        self.root.mainloop()

    def estilos(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background="#ecf0f1", rowheight=25)
        style.configure("Treeview.Heading", background="#e67e22", foreground="white", font=('Arial', 10, 'bold'))

    def crear_widgets(self):
        # HEADER
        header = tk.Frame(self.root, bg="#34495e", height=60)
        header.pack(fill="x")
        tk.Label(header, text="🛡️ GESTIÓN DE GREMIO", font=("Impact", 24), bg="#34495e", fg="#f1c40f").pack(side="left", padx=20)
        f_sys = tk.Frame(header, bg="#34495e")
        f_sys.pack(side="right", padx=10)
        tk.Button(f_sys, text="💾 Guardar", command=self.acc_guardar, bg="#27ae60", fg="white").pack(side="left", padx=2)
        tk.Button(f_sys, text="📂 Cargar", command=self.acc_cargar, bg="#2980b9", fg="white").pack(side="left", padx=2)

        main = tk.Frame(self.root, bg="#2c3e50")
        main.pack(fill="both", expand=True, padx=20, pady=20)

        # -- TABLA HÉROES --
        f_izq = tk.LabelFrame(main, text="Aventureros", bg="#2c3e50", fg="white")
        f_izq.place(x=0, y=0, width=500, height=400)
        cols_h = ("Nombre", "Raza", "Clase", "Nvl", "Fuerza")
        self.tv_h = ttk.Treeview(f_izq, columns=cols_h, show="headings")
        self.tv_h.pack(fill="both", expand=True)
        for c in cols_h: 
            self.tv_h.heading(c, text=c)
            self.tv_h.column(c, width=80)
        
        btn_h = tk.Frame(f_izq, bg="#2c3e50")
        btn_h.pack(fill="x", pady=5)
        tk.Button(btn_h, text="➕ Reclutar Nuevo", command=self.ventana_reclutar, bg="#16a085", fg="white").pack(side="left", fill="x", expand=True, padx=2)
        tk.Button(btn_h, text="✏️ Editar Héroe", command=self.ventana_editar, bg="#e67e22", fg="white").pack(side="left", fill="x", expand=True, padx=2)

        # -- TABLA MISIONES --
        f_der = tk.LabelFrame(main, text="Tablón de Misiones", bg="#2c3e50", fg="white")
        f_der.place(x=520, y=0, width=540, height=400)
        cols_m = ("Rango", "Misión", "Requisitos", "Recompensa", "Estado")
        self.tv_m = ttk.Treeview(f_der, columns=cols_m, show="headings")
        self.tv_m.pack(fill="both", expand=True)
        for c in cols_m: self.tv_m.heading(c, text=c)
        self.tv_m.column("Misión", width=150)
        
        # --- BOTÓN PARA AGREGAR MISIONES ---
        btn_m = tk.Frame(f_der, bg="#2c3e50")
        btn_m.pack(fill="x", pady=5)
        tk.Button(btn_m, text="➕ Publicar Nueva Misión", command=self.ventana_nueva_mision, bg="#c0392b", fg="white").pack(fill="x", padx=2)

        # -- PANEL CONTROL --
        f_ctrl = tk.LabelFrame(self.root, text="Panel de Control", bg="#34495e", fg="white")
        f_ctrl.place(x=20, y=500, width=1060, height=180)
        tk.Button(f_ctrl, text="📜 FIRMAR CONTRATO", command=self.acc_asignar, bg="#f39c12", font=("Arial", 11, "bold")).place(x=20, y=30, width=250, height=50)
        tk.Button(f_ctrl, text="✅ COMPLETAR MISIÓN", command=self.acc_completar, bg="#27ae60", fg="white", font=("Arial", 11, "bold")).place(x=280, y=30, width=250, height=50)
        self.lbl_tesoro = tk.Label(f_ctrl, text="Tesoro: 0", font=("Arial", 20, "bold"), bg="#34495e", fg="#f1c40f")
        self.lbl_tesoro.place(x=800, y=30)
        tk.Label(f_ctrl, text="Consultar Bestiario:", bg="#34495e", fg="white").place(x=20, y=100)
        self.ent_api = tk.Entry(f_ctrl, width=20)
        self.ent_api.place(x=140, y=100)
        tk.Button(f_ctrl, text="🔍 Buscar", command=self.acc_api, bg="#8e44ad", fg="white").place(x=280, y=95)

    # --- VENTANAS ---
    def ventana_reclutar(self):
        top = tk.Toplevel(self.root)
        top.title("Reclutar")
        top.geometry("300x500")
        campos = ["Nombre", "Clase", "Raza", "Fuerza (Num)", "Magia (Num)", "Equipo Inicial"]
        entradas = {}
        for c in campos:
            tk.Label(top, text=c).pack()
            e = tk.Entry(top)
            e.pack()
            entradas[c] = e
        def guardar():
            try:
                if self.mgr.registrar_heroe(entradas["Nombre"].get(), entradas["Clase"].get(), entradas["Raza"].get(), int(entradas["Fuerza (Num)"].get()), int(entradas["Magia (Num)"].get()), entradas["Equipo Inicial"].get()):
                    self.actualizar_tablas()
                    top.destroy()
                else: messagebox.showerror("Error", "Nombre duplicado.")
            except: messagebox.showerror("Error", "Datos numéricos inválidos.")
        tk.Button(top, text="Guardar", command=guardar).pack(pady=10)

    # --- VENTANA PARA CREAR MISIONES ---
    def ventana_nueva_mision(self):
        top = tk.Toplevel(self.root)
        top.title("Publicar Misión")
        top.geometry("300x550")
        
        campos = ["Título", "Rango (E-S)", "Nivel Min", "Fuerza Min", "Oro", "Monstruo Objetivo"]
        entradas = {}
        for c in campos:
            tk.Label(top, text=c).pack(pady=2)
            e = tk.Entry(top)
            e.pack(pady=2)
            entradas[c] = e
            
        def publicar():
            try:
                tit = entradas["Título"].get()
                ran = entradas["Rango (E-S)"].get()
                nvl = int(entradas["Nivel Min"].get())
                fue = int(entradas["Fuerza Min"].get())
                oro = int(entradas["Oro"].get())
                mon = entradas["Monstruo Objetivo"].get()
                
                if tit and ran:
                    self.mgr.publicar_mision(tit, ran, nvl, fue, oro, mon)
                    messagebox.showinfo("Éxito", "Misión publicada.")
                    self.actualizar_tablas()
                    top.destroy()
                else: messagebox.showwarning("Error", "Título y Rango obligatorios.")
            except ValueError: messagebox.showerror("Error", "Nivel, Fuerza y Oro deben ser números.")
            
        tk.Button(top, text="Publicar", command=publicar, bg="#c0392b", fg="white").pack(pady=20)

    def ventana_editar(self):
        sel = self.tv_h.selection()
        if not sel: return
        nombre = self.tv_h.item(sel[0])['values'][0]
        h = self.mgr.buscar_heroe(nombre)
        top = tk.Toplevel(self.root)
        top.title(f"Editando {nombre}")
        top.geometry("300x300")
        tk.Label(top, text="Equipo:").pack()
        e_eq = tk.Entry(top); e_eq.insert(0, h.equipo); e_eq.pack()
        tk.Label(top, text="Fuerza:").pack()
        e_fu = tk.Entry(top); e_fu.insert(0, h.fuerza); e_fu.pack()
        tk.Label(top, text="Magia:").pack()
        e_ma = tk.Entry(top); e_ma.insert(0, h.magia); e_ma.pack()
        def save():
            self.mgr.editar_heroe(nombre, e_eq.get(), e_fu.get(), e_ma.get())
            self.actualizar_tablas(); top.destroy()
        tk.Button(top, text="Actualizar", command=save).pack(pady=10)

    def actualizar_tablas(self):
        for i in self.tv_h.get_children(): self.tv_h.delete(i)
        for h in self.mgr.aventureros: self.tv_h.insert("", "end", values=(h.nombre, h.raza, h.clase, h.nivel, h.fuerza))
        for i in self.tv_m.get_children(): self.tv_m.delete(i)
        for m in self.mgr.misiones: self.tv_m.insert("", "end", values=m.get_info_tablero())
        self.lbl_tesoro.config(text=f"Tesoro: {self.mgr.cofre}")

    def acc_asignar(self):
        sh, sm = self.tv_h.selection(), self.tv_m.selection()
        if sh and sm:
            res = self.mgr.asignar_mision(self.tv_h.item(sh[0])['values'][0], self.tv_m.item(sm[0])['values'][1])
            messagebox.showinfo("Info", res); self.actualizar_tablas()
        else: messagebox.showwarning("!", "Selecciona Héroe y Misión.")

    def acc_completar(self):
        sm = self.tv_m.selection()
        if sm:
            res = self.mgr.reportar_exito(self.tv_m.item(sm[0])['values'][1])
            messagebox.showinfo("Info", res); self.actualizar_tablas()

    def acc_guardar(self): messagebox.showinfo("Sys", self.mgr.guardar())
    def acc_cargar(self): messagebox.showinfo("Sys", self.mgr.cargar()); self.actualizar_tablas()
    def acc_api(self):
        q = self.ent_api.get()
        if q: messagebox.showinfo("API", self.mgr.consulta_api(q))

if _name_ == "_main_":
    gm = GremioManager("Eshmaluguls")
    gm.registrar_heroe("Leonardo", "Paladín", "Humano", 15, 5, "Espada")
    gm.publicar_mision("Ratas", "D", 1, 0, 50, "rat")
    GuildGUI(gm)