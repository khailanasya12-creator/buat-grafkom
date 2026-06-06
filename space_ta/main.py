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
preview_player = None  

def clear_landing_page():
    for item in landing_page_entities:
        item.enabled = False

def show_landing_page():
    clear_skin_menu()
    for item in landing_page_entities:
        item.enabled = True

def clear_skin_menu():
    global preview_player
    for item in skin_menu_entities:
        item.enabled = False
    if preview_player:
        destroy(preview_player)
        preview_player = None

def create_menus():
    global landing_page_entities, skin_menu_entities
    
    # ------------------ A. ELEMEN LANDING PAGE ------------------
    title = Text(text="SPACE SHOOTER", font=FONT_PATH, origin=(0,0), y=2.5, scale=6, color=color.cyan)
    landing_page_entities.append(title)
    
    # Tombol START GAME
    start_btn = Button(
        text="Start Game",
        color=color.rgba(1, 1, 1, 0.8),
        scale=(4, 0.8),
        y=0.3,
        radius=0.25,
        highlight_color=color.rgba(180/255, 30/255, 30/255, 0.8)
    )
    start_btn.text_entity.font = FONT_PATH
    start_btn.text_entity.color = color.rgb(128/255, 0, 0)
    start_btn.text_entity.scale = 1.5
    start_btn.on_click = start_game
    landing_page_entities.append(start_btn)
    
    # Tombol PILIH SKIN
    skin_menu_btn = Button(
        text="Pilih Skin",
        color=color.rgba(1, 1, 1, 0.8),
        scale=(4, 0.8),
        y=-0.7,
        radius=0.25,
        highlight_color=color.rgba(180/255, 30/255, 30/255, 0.8)
    )
    skin_menu_btn.text_entity.font = FONT_PATH
    skin_menu_btn.text_entity.color = color.rgb(128/255, 0, 0)
    skin_menu_btn.text_entity.scale = 1.5
    skin_menu_btn.on_click = open_skin_menu
    landing_page_entities.append(skin_menu_btn)


    # ------------------ B. ELEMEN MENU PILIH SKIN ------------------
    skin_title = Text(text="PILIH SKIN PESAWAT", font=FONT_PATH, origin=(0,0), y=3, scale=4, color=color.white)
    skin_title.enabled = False
    skin_menu_entities.append(skin_title)
    
    def change_skin(texture_path):
        global selected_texture, preview_player
        selected_texture = texture_path
        if preview_player:
            preview_player.texture = texture_path

    # Skin 1
    img_s1 = Entity(model='quad', texture='assets/Missile_01.png', rotation_z=-90, scale=1.2, position=(-4, 0.5, -1))
    btn_s1 = Button(text="Skin 1", color=color.rgba(0,0,0,0.3), scale=(1.8, 0.5), position=(-4, -0.6), highlight_color=color.cyan)
    btn_s1.text_entity.font = FONT_PATH
    btn_s1.on_click = Func(change_skin, 'assets/Missile_01.png')
    img_s1.enabled = btn_s1.enabled = False
    skin_menu_entities.extend([img_s1, btn_s1])
    
    # Skin 2
    img_s2 = Entity(model='quad', texture='assets/Missile_02.png', rotation_z=-90, scale=1.2, position=(0, 0.5, -1))
    btn_s2 = Button(text="Skin 2", color=color.rgba(0,0,0,0.3), scale=(1.8, 0.5), position=(0, -0.6), highlight_color=color.cyan)
    btn_s2.text_entity.font = FONT_PATH
    btn_s2.on_click = Func(change_skin, 'assets/Missile_02.png')
    img_s2.enabled = btn_s2.enabled = False
    skin_menu_entities.extend([img_s2, btn_s2])
    
    # Skin 3
    img_s3 = Entity(model='quad', texture='assets/Missile_03.png', rotation_z=-90, scale=1.2, position=(4, 0.5, -1))
    btn_s3 = Button(text="Skin 3", color=color.rgba(0,0,0,0.3), scale=(1.8, 0.5), position=(4, -0.6), highlight_color=color.cyan)
    btn_s3.text_entity.font = FONT_PATH
    btn_s3.on_click = Func(change_skin, 'assets/Missile_03.png')
    img_s3.enabled = btn_s3.enabled = False
    skin_menu_entities.extend([img_s3, btn_s3])

    # Tombol OK
    ok_btn = Button(text="OK", color=color.green, scale=(2, 0.6), position=(-1.5, -2.2), highlight_color=color.lime)
    ok_btn.text_entity.font = FONT_PATH
    ok_btn.on_click = show_landing_page
    ok_btn.enabled = False
    skin_menu_entities.append(ok_btn)

    # Tombol BACK
    back_btn = Button(text="Back", color=color.red, scale=(2, 0.6), position=(1.5, -2.2), highlight_color=color.orange)
    back_btn.text_entity.font = FONT_PATH
    back_btn.on_click = show_landing_page
    back_btn.enabled = False
    skin_menu_entities.append(back_btn)


def open_skin_menu():
    global preview_player
    clear_landing_page()
    for item in skin_menu_entities:
        item.enabled = True
    preview_player = Entity(model='quad', texture=selected_texture, rotation_z=-90, scale=0.8, position=(0, 2, -1))

def start_game():
    global game_started
    game_started = True
    clear_landing_page()
    clear_skin_menu()
    player.texture = selected_texture
    player.enabled = True
    score_text.text = f'Score: {score}'
    hp_text.text = f'HP: {player_hp}'
    spawn_enemy()
    alien_nembak()
    spawn_planet()


# Nyalakan menu utama di awal
create_menus()
app.run()