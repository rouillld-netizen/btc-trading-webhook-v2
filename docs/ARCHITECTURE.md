# Architecture du moteur de trading

## Principe général

TradingView reste le cerveau de la stratégie.

Le serveur reçoit des événements, vérifie leur validité, puis demande à l'exchange d'exécuter l'action.

## Flux

TradingView
→ Webhook FastAPI
→ TradeEngine
→ ExchangeAdapter
→ Coinbase / Binance

## Responsabilités

### TradingView

- Détecte les signaux
- Décide des ouvertures
- Définit le SL initial
- Définit le TP initial
- Modifie les niveaux de SL / TP

### FastAPI

- Reçoit les webhooks
- Vérifie le secret
- Valide le JSON
- Transmet l'événement au TradeEngine

### TradeEngine

- Interprète les actions TradingView
- Vérifie l'état actuel de la position
- Calcule la taille si nécessaire
- Empêche les doublons
- Demande à l'exchange d'exécuter l'action

### ExchangeAdapter

- Fournit une interface commune :
  - get_balance
  - get_position
  - get_open_orders
  - open_long
  - open_short
  - update_protection_order
  - cancel_protection_order

### CoinbaseAPI

- Traduit les actions en requêtes Coinbase
- Connaît les product_id Coinbase
- Connaît les payloads Coinbase
- Ne contient pas de logique de stratégie

## Actions webhook prévues

### OPEN_LONG

Ouvre une position longue avec SL et éventuellement TP.

### OPEN_SHORT

Ouvre une position courte avec SL et éventuellement TP.

### UPDATE_SL

Déplace le stop loss.

### UPDATE_TP

Déplace le take profit.

### UPDATE_PROTECTION

Met à jour SL et TP en une seule action.

## Règle importante

TradingView ne ferme pas les positions directement.

Les positions se ferment via SL ou TP sur l'exchange.
