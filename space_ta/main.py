from ursina import *
import random

app = Ursina()

# --- 1. SETUP KAMERA & BACKGROUND ---
camera.orthographic = True
camera.fov = 10 

# Memanggil background utama game
bg = Entity(
    model='quad', 
    texture='background/bckground.png', 
    scale=(25, 15), 
    z=2, 
    color=color.white
)

# --- Jalur Font Kustom Kamu ---
FONT_PATH = 'assets/fonts/heaters.otf'

# --- Variabel Global Status Game ---
score = 0               
player_hp = 3           
game_over = False       
game_started = False    # Menandakan apakah game sudah mulai bermain atau masih di menu
selected_texture = 'assets/Missile_01.png'   # Menyimpan roket pilihan pemain (default skin 1)

# --- UI Text Game (Skor & HP) ---
score_text = Text(text='', font=FONT_PATH, position=(-0.85, 0.45), scale=3, color=color.yellow)
hp_text = Text(text='', font=FONT_PATH, position=(0.7, 0.45), scale=3, color=color.red)
game_over_text = Text(text='', font=FONT_PATH, position=(-0.25, 0), scale=5, color=color.red)

# --- 2. SETUP KARAKTER (PEMAIN) ---
player = Entity(
    model='quad', 
    scale=(1.2, 1.2), 
    position=(-6, 0), 
    rotation_z=-90,     # Memutar roket menghadap ke kanan
    collider='box',
    color=color.white,
    enabled=False       # Dimatikan dulu sebelum game dimulai
)

# List penampung objek game
bullets = []        
enemies = []        
enemy_bullets = []  
planets = []        


# --- 3. LOGIKA UTAMA GAME (UPDATE PER FRAME) ---
def update():
    global score, player_hp, game_over
    
    # Jangan jalankan logika game jika belum mulai atau sudah game over
    if not game_started or game_over:
        return 

    # A. Gerakan Pemain (W, A, S, D)
    player.y += (held_keys['w'] - held_keys['s']) * 7 * time.dt
    player.x += (held_keys['d'] - held_keys['a']) * 7 * time.dt
    
    player.y = clamp(player.y, -4.5, 4.5)
    player.x = clamp(player.x, -8, 8)

    # B. Peluru Pemain melaju ke Kanan
    for b in bullets[:]:
        b.x += 15 * time.dt
        if b.x > 10:
            bullets.remove(b)
            destroy(b)

    # C. Musuh & Asteroid maju ke Kiri & Cek Tabrakan
    for e in enemies[:]:
        e.x -= 6 * time.dt 
        
        if 'astero' in e.texture.name or 'abstrak' in e.texture.name:
            e.rotation_z += 50 * time.dt
        
        if e.x < -10:
            enemies.remove(e)
            destroy(e)
            continue

        hit_info = e.intersects()
        if hit_info.hit:
            if hit_info.entity in bullets:
                bullets.remove(hit_info.entity)
                destroy(hit_info.entity) 
                enemies.remove(e)
                destroy(e) 
                score += 10 
                score_text.text = f'Score: {score}'

        if e.intersects(player).hit:
            enemies.remove(e)
            destroy(e)
            kurangi_hp()

    # D. Peluru Musuh melaju ke Kiri
    for eb in enemy_bullets[:]:
        eb.x -= 10 * time.dt 
        
        if eb.x < -10:
            enemy_bullets.remove(eb)
            destroy(eb)
            continue
            
        if eb.intersects(player).hit:
            enemy_bullets.remove(eb)
            destroy(eb)
            kurangi_hp()

    # E. Pergerakan Hiasan Planet di Latar Belakang
    for p in planets[:]:
        p.x -= 1 * time.dt 
        if p.x < -15:
            planets.remove(p)
            destroy(p)


# --- 4. KONTROL INPUT TEMBAKAN ---
def input(key):
    if not game_started or game_over: 
        return
        
    if key == 'space':
        b = Entity(
            model='quad', 
            texture='assets/laser.png', 
            scale=(1.5, 0.4), 
            position=player.position + Vec3(1.5, 0, 0), 
            collider='box',
            color=color.white
        )
        bullets.append(b)


# --- 5. SISTEM SPAWN TARGET (ALIEN & ASTEROID) ---
def spawn_enemy():
    if not game_started or game_over: return
    
    daftar_target = [
        'assets/abstrak.png', 'assets/astero1.png', 'assets/astero2.png', 
        'assets/astero3.png', 'assets/astero4.png', 'assets/astero5.png',
        'assets/ufo.png', 'assets/ufo2.png'
    ]
    pilihan_aset = random.choice(daftar_target)
    
    e = Entity(
        model='quad', 
        texture=pilihan_aset, 
        scale=(1.3, 1.3), 
        position=(10, random.uniform(-4, 4)), 
        collider='box',
        color=color.white
    )
    enemies.append(e)
    invoke(spawn_enemy, delay=random.uniform(0.7, 1.5))


# --- 6. SISTEM ALIEN MENEMBAK ---
def alien_nembak():
    if not game_started or game_over: return
    
    alien_di_layar = [a for a in enemies if 'ufo' in a.texture.name]
    
    if len(alien_di_layar) > 0:
        penembak = random.choice(alien_di_layar)
        
        eb = Entity(
            model='quad', 
            texture='assets/fanas.png', 
            scale=(0.8, 0.8), 
            position=penembak.position - Vec3(1, 0, 0), 
            collider='box',
            color=color.white, 
            rotation_z=180 
        )
        enemy_bullets.append(eb)
        
    invoke(alien_nembak, delay=random.uniform(1.2, 2.5))


# --- 7. SISTEM SPAWN PLANET BACKGROUND ---
def spawn_planet():
    if not game_started or game_over: return
    
    daftar_planet = ['assets/bumi.png', 'assets/mars.png', 'assets/venus.png', 'assets/blackhole.png']
    planet_terpilih = random.choice(daftar_planet)
    
    p = Entity(
        model='quad',
        texture=planet_terpilih,
        scale=(random.uniform(2.0, 3.5)), 
        position=(15, random.uniform(-4, 4)),
        z=1, 
        color=color.white
    )
    planets.append(p)
    invoke(spawn_planet, delay=random.uniform(5.0, 10.0))


# --- 8. LOGIKA HP & NYAWA ---
def kurangi_hp():
    global player_hp, game_over
    player_hp -= 1
    hp_text.text = f'HP: {player_hp}'
    
    if player_hp <= 0:
        game_over = True
        game_over_text.text = 'GAME OVER'
        destroy(player)


# --- 9. SISTEM MANAJEMEN MENU (LANDING PAGE & SKIN SELECTION) ---
landing_page_entities = []
skin_menu_entities = []

def clear_landing_page():
    for item in landing_page_entities:
        item.enabled = False

def show_landing_page():
    clear_skin_menu()
    for item in landing_page_entities:
        item.enabled = True

def clear_skin_menu():
    for item in skin_menu_entities:
        item.enabled = False

def create_menus():
    global landing_page_entities, skin_menu_entities

    # ===== LANDING PAGE =====
    title = Text(
        text="SPACE SHOOTER",
        position=(0, 0.35),
        origin=(0,0),
        scale=3,
        color=color.cyan
    )
    landing_page_entities.append(title)

    start_btn = Button(
        text="START GAME",
        scale=(0.35,0.08),
        position=(0,0.05),
        color=color.azure
    )
    start_btn.on_click = start_game
    landing_page_entities.append(start_btn)

    skin_btn = Button(
        text="CHOOSE SKIN",
        scale=(0.35,0.08),
        position=(0,-0.10),
        color=color.orange
    )
    skin_btn.on_click = open_skin_menu
    landing_page_entities.append(skin_btn)

    # ===== MENU SKIN =====
    skin_title = Text(
        text="PILIH ROKET",
        position=(0,0.35),
        origin=(0,0),
        scale=2,
        color=color.white,
        enabled=False
    )
    skin_menu_entities.append(skin_title)

    def change_skin(texture_path):
        global selected_texture
        selected_texture = texture_path

    skins = [
        ('assets/Missile_01.png', -0.3),
        ('assets/Missile_02.png', 0),
        ('assets/Missile_03.png', 0.3)
    ]

    for texture_path, pos_x in skins:
        rocket = Entity(
            model='quad',
            texture=texture_path,
            rotation_z=-90,
            scale=1.2,          # <--- DIUBAH JADI 1.2 BIAR GAK KECIL LAGI
            position=(pos_x * 12, 0.5),
            enabled=False
        )

        btn = Button(
            text='PILIH',
            scale=(0.12, 0.05),
            position=(pos_x, -0.12),
            enabled=False
        )
        btn.on_click = Func(change_skin, texture_path)

        skin_menu_entities.append(rocket)
        skin_menu_entities.append(btn)

    ok_btn = Button(
        text="OK",
        scale=(0.15,0.06),
        position=(-0.12,-0.3),
        color=color.green,
        enabled=False
    )
    ok_btn.on_click = show_landing_page
    skin_menu_entities.append(ok_btn)

    back_btn = Button(
        text="BACK",
        scale=(0.15,0.06),
        position=(0.12,-0.3),
        color=color.red,
        enabled=False
    )
    back_btn.on_click = show_landing_page
    skin_menu_entities.append(back_btn)


def open_skin_menu():
    clear_landing_page()
    for item in skin_menu_entities:
        item.enabled = True

def start_game():
    global game_started
    game_started = True
    clear_landing_page()
    clear_skin_menu()
    player.texture = selected_texture
    player.scale = (1.2, 1.2)   # <--- KUNCI UKURAN PLAYER BIAR GA RAKSASA PAS MAIN!
    player.enabled = True
    score_text.text = f'Score: {score}'
    hp_text.text = f'HP: {player_hp}'
    spawn_enemy()
    alien_nembak()
    spawn_planet()


# Nyalakan menu utama di awal
create_menus()
app.run()