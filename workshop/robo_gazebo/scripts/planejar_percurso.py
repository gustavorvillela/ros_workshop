#!/usr/bin/env python3
"""Aula 7 — confere, antes de abrir o Gazebo, se um percurso de cilindros funciona.

Lê as paredes, os obstáculos e os cilindros de um mundo SDF e simula, de forma ideal, o
que o cylinder_follower faz para cada cor da sequência:
  1. gira para a esquerda (w_busca > 0) até o cilindro aparecer na câmera, sem nada na frente;
  2. alinha e anda reto até parar com a câmera a 1,5 m da superfície do cilindro.
Depois aponta os problemas e desenha o plano numa figura.

Uso (no contêiner ou no computador, com matplotlib):
  python3 planejar_percurso.py ../worlds/sala2.sdf verde azul amarelo vermelho
  python3 planejar_percurso.py ../worlds/sala2.sdf verde azul amarelo vermelho -o plano.png

É uma conta geométrica, não uma simulação: confirme sempre no Gazebo.
"""
import argparse
import math
import xml.etree.ElementTree as ET

# Geometria do robô e do cylinder_follower (Aulas 2, 4 e 6)
COMPRIMENTO, LARGURA = 2.0, 1.0      # m: chassi
CAMERA = 1.03                        # m: câmera à frente do centro do robô
PARADA = 1.5                         # m: parâmetro 'distancia' do follower (câmera → superfície)
FOV = math.radians(35)               # metade do campo de visão útil (a câmera tem 80°)
ALCANCE_CAMERA = 15.0                # m: mais longe que isso o cilindro fica pequeno demais
ALCANCE_LIDAR = 10.0                 # m: alcance do lidar do robô (para a cobertura do mapa)
R_GIRO = math.hypot(COMPRIMENTO / 2, LARGURA / 2)   # raio varrido ao girar no lugar
MARGEM = 0.3                         # m: folga mínima que consideramos segura


def ler_mundo(arquivo):
    """Devolve (caixas, cilindros): caixas = [(nome, cx, cy, sx, sy)], cilindros = {cor: (x, y, r)}."""
    caixas, cilindros = [], {}
    for modelo in ET.parse(arquivo).getroot().iter('model'):
        nome = modelo.get('name')
        pose = modelo.find('pose')
        x, y = (float(v) for v in pose.text.split()[:2]) if pose is not None else (0.0, 0.0)
        box = modelo.find('.//collision/geometry/box/size')
        cil = modelo.find('.//collision/geometry/cylinder/radius')
        if box is not None:
            sx, sy = (float(v) for v in box.text.split()[:2])
            caixas.append((nome, x, y, sx, sy))
        elif cil is not None and nome.startswith('cilindro_'):
            cilindros[nome[len('cilindro_'):]] = (x, y, float(cil.text))
    return caixas, cilindros


def dist_caixa(px, py, c):
    _, cx, cy, sx, sy = c
    return math.hypot(max(abs(px - cx) - sx / 2, 0.0), max(abs(py - cy) - sy / 2, 0.0))


def dist_obstaculo(px, py, caixas, cilindros):
    d = min((dist_caixa(px, py, c) for c in caixas), default=99.0)
    for (x, y, r) in cilindros:
        d = min(d, math.hypot(px - x, py - y) - r)
    return d


def visada_livre(x0, y0, x1, y1, caixas, cilindros):
    n = max(int(math.hypot(x1 - x0, y1 - y0) / 0.05), 1)
    for k in range(1, n):
        t = k / n
        if dist_obstaculo(x0 + t * (x1 - x0), y0 + t * (y1 - y0), caixas, cilindros) <= 0.0:
            return False
    return True


def pontos_corpo(x, y, th):
    for a in (-1.0, -0.5, 0.0, 0.5, 1.0):
        for b in (-0.5, -0.25, 0.0, 0.25, 0.5):
            yield (x + a * math.cos(th) - b * math.sin(th), y + a * math.sin(th) + b * math.cos(th))


def planejar(caixas, cilindros, sequencia, x=0.0, y=0.0, th=0.0):
    problemas, trechos = [], []
    for cor in sequencia:
        if cor not in cilindros:
            problemas.append(f'{cor}: não há cilindro_{cor} no mundo')
            continue
        cx, cy, r = cilindros[cor]
        outros = [v for k, v in cilindros.items() if k != cor]
        folga_giro = dist_obstaculo(x, y, caixas, list(cilindros.values())) - R_GIRO
        if folga_giro < MARGEM:
            problemas.append(f'antes do {cor}: pouco espaço para girar em ({x:.1f}, {y:.1f}): '
                             f'folga de {folga_giro:.2f} m, precisa de {MARGEM} m')
        girou, achou = 0.0, False
        while girou <= 2 * math.pi:
            camx, camy = x + CAMERA * math.cos(th), y + CAMERA * math.sin(th)
            ang = math.atan2(cy - camy, cx - camx) - th
            ang = math.atan2(math.sin(ang), math.cos(ang))
            if (abs(ang) < FOV and math.hypot(cx - camx, cy - camy) < ALCANCE_CAMERA
                    and visada_livre(camx, camy, cx, cy, caixas, outros)):
                achou = True
                break
            th += 0.02
            girou += 0.02
        if not achou:
            problemas.append(f'{cor}: a câmera não o vê de ({x:.1f}, {y:.1f}) em nenhuma direção '
                             '(parede ou cilindro no caminho, ou longe demais)')
            continue
        th = math.atan2(cy - y, cx - x)
        anda = math.hypot(cx - x, cy - y) - (PARADA + r + CAMERA)
        if anda < 0:
            problemas.append(f'{cor}: o robô já começa perto demais ({-anda:.1f} m além da parada)')
            anda = 0.0
        pior = 99.0
        for k in range(int(anda / 0.05) + 1):
            px, py = x + k * 0.05 * math.cos(th), y + k * 0.05 * math.sin(th)
            for p in pontos_corpo(px, py, th):
                pior = min(pior, dist_obstaculo(*p, caixas, outros))
        if pior < MARGEM:
            problemas.append(f'indo ao {cor}: o robô passa a {max(pior, 0):.2f} m de um obstáculo '
                             f'(precisa de {MARGEM} m)')
        nx, ny = x + anda * math.cos(th), y + anda * math.sin(th)
        trechos.append(dict(cor=cor, de=(x, y), ate=(nx, ny), th=th, girou=girou, anda=anda, folga=pior))
        x, y = nx, ny
    return problemas, trechos


def cobertura(caixas, trechos):
    """Fração da área livre que o lidar alcança (com visada livre) de algum ponto do percurso."""
    xs = [c[1] for c in caixas]
    ys = [c[2] for c in caixas]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    pontos = []
    for t in trechos:
        (ax, ay), (bx, by) = t['de'], t['ate']
        n = max(int(math.hypot(bx - ax, by - ay) / 1.0), 1)
        pontos += [(ax + (bx - ax) * k / n, ay + (by - ay) * k / n) for k in range(n + 1)]
    livres = vistas = 0
    y = y0 + 0.5
    while y < y1:
        x = x0 + 0.5
        while x < x1:
            if dist_obstaculo(x, y, caixas, []) > 0:
                livres += 1
                if any(math.hypot(x - px, y - py) < ALCANCE_LIDAR and
                       visada_livre(px, py, x, y, caixas, []) for px, py in pontos):
                    vistas += 1
            x += 1.0
        y += 1.0
    return vistas / max(livres, 1)


def desenhar(caixas, cilindros, trechos, arquivo):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Polygon, Rectangle
    rgb = {'vermelho': '#cc1a1a', 'verde': '#1ab31a', 'azul': '#1a33cc', 'amarelo': '#e6cc1a'}
    fig, ax = plt.subplots(figsize=(10, 7), dpi=130)
    for (_, cx, cy, sx, sy) in caixas:
        ax.add_patch(Rectangle((cx - sx / 2, cy - sy / 2), sx, sy, color='#777777'))
    for cor, (x, y, r) in cilindros.items():
        ax.add_patch(Circle((x, y), r, color=rgb.get(cor, '#999999'), zorder=3))
    for i, t in enumerate(trechos, 1):
        (ax_, ay), (bx, by) = t['de'], t['ate']
        ax.annotate('', xy=(bx, by), xytext=(ax_, ay),
                    arrowprops=dict(arrowstyle='->', color=rgb.get(t['cor'], 'k'), lw=2))
        ax.add_patch(Circle((ax_, ay), R_GIRO, fill=False, ls=':', color='#555555'))
        c, s = math.cos(t['th']), math.sin(t['th'])
        canto = [(bx + a * c - b * s, by + a * s + b * c) for a, b in
                 ((-1, -0.5), (1, -0.5), (1, 0.5), (-1, 0.5))]
        ax.add_patch(Polygon(canto, fill=False, color=rgb.get(t['cor'], 'k'), lw=1.2))
        ax.text(bx, by + 0.7, str(i), ha='center', fontsize=10, weight='bold')
    ax.plot(0, 0, 'k^', ms=10)
    ax.text(0, -0.8, 'início', ha='center', fontsize=9)
    ax.set_aspect('equal')
    ax.autoscale()
    ax.set_xlabel('x (m)')
    ax.set_ylabel('y (m)')
    ax.grid(alpha=0.3)
    ax.set_title('Plano do percurso: setas = trechos retos, retângulos = onde o robô para, '
                 'pontilhado = giro', fontsize=9)
    fig.tight_layout()
    fig.savefig(arquivo)


def main():
    ap = argparse.ArgumentParser(description='Confere um percurso de cilindros num mundo SDF.')
    ap.add_argument('mundo', help='arquivo .sdf do mundo')
    ap.add_argument('sequencia', nargs='+', help='cores na ordem de visita')
    ap.add_argument('-o', '--figura', default='plano_percurso.png', help='figura de saída')
    a = ap.parse_args()
    caixas, cilindros = ler_mundo(a.mundo)
    problemas, trechos = planejar(caixas, cilindros, a.sequencia)
    for i, t in enumerate(trechos, 1):
        print(f'{i}. {t["cor"]:9s} gira {math.degrees(t["girou"]):4.0f}°, anda {t["anda"]:4.1f} m e para em '
              f'({t["ate"][0]:5.1f}, {t["ate"][1]:5.1f}); folga mínima no caminho {t["folga"]:.2f} m')
    print(f'Cobertura estimada do lidar ao longo do percurso: {100 * cobertura(caixas, trechos):.0f}% da área livre')
    desenhar(caixas, cilindros, trechos, a.figura)
    print(f'Figura: {a.figura}')
    if problemas:
        print('\nPROBLEMAS:')
        for p in problemas:
            print('  - ' + p)
        raise SystemExit(1)
    print('Nenhum problema encontrado.')


if __name__ == '__main__':
    main()
