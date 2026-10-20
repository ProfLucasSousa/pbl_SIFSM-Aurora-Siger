-- =====================================================
-- SIFSM - AURORA SIGER
-- Banco de dados SQLite
-- =====================================================

PRAGMA foreign_keys = ON;

-- Tabela de módulos

CREATE TABLE IF NOT EXISTS modulos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    tipo TEXT NOT NULL,
    consumo_kw REAL NOT NULL CHECK(consumo_kw >= 0),
    prioridade INTEGER NOT NULL
        CHECK(prioridade BETWEEN 1 AND 5),
    status TEXT NOT NULL
        CHECK(status IN ('ativo', 'manutencao', 'alerta'))
);

-- Tabela de leituras dos sensores

CREATE TABLE IF NOT EXISTS leituras_sensores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    modulo_id INTEGER NOT NULL,
    ciclo_horas REAL NOT NULL,
    geracao_kw REAL NOT NULL,
    consumo_kw REAL NOT NULL,
    umidade_percentual REAL,
    agua_percentual REAL,
    temperatura_c REAL,
    sensores_validos INTEGER NOT NULL,

    FOREIGN KEY (modulo_id)
        REFERENCES modulos(id)
        ON DELETE CASCADE
);

-- Tabela de alertas

CREATE TABLE IF NOT EXISTS alertas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    modulo_id INTEGER NOT NULL,
    descricao TEXT NOT NULL,
    prioridade INTEGER NOT NULL
        CHECK(prioridade BETWEEN 1 AND 5),
    status TEXT NOT NULL,

    FOREIGN KEY (modulo_id)
        REFERENCES modulos(id)
        ON DELETE CASCADE
);

-- =====================================================
-- CADASTRO INICIAL DOS MÓDULOS
-- =====================================================

INSERT OR IGNORE INTO modulos
(nome, tipo, consumo_kw, prioridade, status)
VALUES
('Habitação', 'suporte_vida', 35, 5, 'ativo'),

('Centro de Controle', 'controle', 30, 5, 'ativo'),

('Armazenamento de Energia', 'energia', 10, 5, 'ativo'),

('Agricultura', 'agricultura', 40, 4, 'ativo'),

('Laboratório Científico', 'pesquisa', 25, 3, 'ativo'),

('Comunicação', 'comunicacao', 20, 4, 'ativo'),

('Suporte Médico', 'saude', 30, 5, 'ativo'),

('Produção de Oxigênio', 'suporte_vida', 45, 5, 'ativo');

-- =====================================================
-- ALERTAS INICIAIS
-- =====================================================

INSERT INTO alertas
(modulo_id, descricao, prioridade, status)
SELECT
    id,
    'Verificar eficiência dos sistemas de armazenamento.',
    3,
    'pendente'
FROM modulos
WHERE nome = 'Armazenamento de Energia';

INSERT INTO alertas
(modulo_id, descricao, prioridade, status)
SELECT
    id,
    'Monitorar condições ambientais da agricultura.',
    4,
    'pendente'
FROM modulos
WHERE nome = 'Agricultura';