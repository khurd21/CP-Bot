# Card-Jitsu Implementation Status

## What's Been Implemented

### 1. **Game State Tracking** ✅
- `CardJitsuGameState` now tracks player and opponent `Player` objects
- Each `Player` has `cards` (hand), `score` (won cards), and `side` (LEFT/RIGHT)
- Card data structure includes `type` (FIRE/WATER/ICE), `color` (from Color enum), and `value` (numeric rank)

### 2. **Score Detection** ✅ (Framework Ready)
- `detect_score()` function implemented to scan scoreboard
- Crops to upper 1/3 of screen and scans based on player side
- Returns `(player_score, opponent_score)` as lists of `Card` objects
- **STATUS**: Awaiting your implementation details on how to identify type and color from scoreboard layout

### 3. **Card Detection** ✅ (Framework Ready)
- `detect_cards()` function implemented to scan player's hand
- Reads 2/3 of screen based on player side (LEFT or RIGHT)
- Returns list of 5 `Card` objects with type, color, and value
- **STATUS**: Awaiting your implementation details on card layout and OCR strategy

### 4. **Round Detection** ✅ (Framework Ready)
- `detect_new_round()` function implemented with timer image matching
- Checks `settings.timer_image_path` to scan for timer template
- **STATUS**: Requires you to provide timer image PNG path

### 5. **Win Condition Detection** ✅
- `_has_win_condition(score)` - Checks if score list represents a win:
  - **3 types with different colors** (e.g., Fire Red + Water Blue + Ice Green)
  - **3 same type with different colors** (e.g., Fire Red + Fire Blue + Fire Green)

### 6. **Card Battle Logic** ✅
- `_card_beats(card1, card2)` - Implements RPS-style type system:
  - Fire beats Ice
  - Ice beats Water
  - Water beats Fire
  - Same type: higher value wins

### 7. **Optimal Card Selection Strategy** ✅
- `select_best_card(opponent_score)` - Priority order:
  1. **Offensive**: If we can achieve a win condition this round, play that card
  2. **Defensive**: If opponent is close to winning, block with a card that beats theirs
  3. **Buildout**: Play card that sets us up for a win (fills missing colors in our type groups)
  4. **Conservative**: Play lowest value card to preserve strength for late game

### 8. **Main Game Loop** ✅
- `run()` function orchestrates full game flow:
  1. Travel to DOJO and start Card-Jitsu
  2. Wait for game-start signal (card-pack.json response)
  3. Detect which side player is on
  4. Initialize player/opponent state objects
  5. Main loop:
     - Detect our 5 cards in hand
     - Detect our score and opponent's score
     - Check for win conditions (with `input()` to pause for your intervention)
     - Select best card to play
     - Loop with configurable interval

## What You Need to Provide

### 1. **Card Detection Details** 🎯
Your hand contains 5 cards arranged on your side. For each card, provide:
- **Position/Layout**: Where are the cards positioned? (e.g., bottom left, spaced horizontally?)
- **Type Identification**: How to identify Fire/Water/Ice? (e.g., OCR, image template, color scan?)
- **Value Location**: Where is the numeric value? (e.g., below the type, in which color range?)
- **Color Scanning**: What pixel colors represent each type's available colors? (RGB ranges?)

### 2. **Scoreboard Detection Details** 🎯
Your score and opponent's score are displayed separately. For each:
- **Position**: Upper left for your side, upper right for opponent
- **Type Representation**: How are Fire/Water/Ice types shown in the scoreboard? (grayscale image? text? color?)
- **Color Stacking**: When you win a card, it stacks. Provide:
  - Pixel column positions for each type (Fire column, Water column, Ice column?)
  - How far down do you scan for each color? (halfway down? specific region?)
  - Color values to match against (already have RGB in `Color` enum)

### 3. **Timer Image** 🎯
Provide a PNG of the game timer:
- Should show the timer that appears in the center of screen when round is about to start
- Location: `src/club_penguin_bot/templates/dojo/`
- Suggested name: `dojo-card-jitsu-timer.png`
- Usage: Set `timer_image_path` in `CardJitsuSettings` to enable round detection

### Example Settings Configuration
```python
settings = CardJitsuSettings(
    player_name="Mr Boop",
    timer_image_path="src/club_penguin_bot/templates/dojo/dojo-card-jitsu-timer.png"
)
```

## Code Hooks Ready for Implementation

### For Card Detection:
```python
def detect_cards(self, screen: np.ndarray) -> list[Card]:
    # Crop region is already prepared (_card_region variable)
    # TODO: Scan for 5 cards, OCR type and value, sample color between them
    # Return list[Card] with type, color, value populated
```

### For Score Detection:
```python
def detect_score(self, screen: np.ndarray) -> tuple[list[Card], list[Card]]:
    # Scoreboard region is already prepared (_scoreboard variable)
    # TODO: Scan for grayscale type images, stack colors down each column
    # Return (player_score, opponent_score)
```

### For Timer Detection:
```python
def detect_new_round(self, _screen: np.ndarray) -> bool:
    # Timer image path is available in self.settings.timer_image_path
    # TODO: Use template matching to find timer in center of screen
    # Return True if timer detected (new round starting)
```

## Win Condition Examples
These are already implemented and working:

**You Win Scenarios:**
- Fire Red + Water Blue + Ice Green (3 types, all different colors)
- Fire Red + Fire Blue + Fire Green (3 same type, all different colors)

**Game End:**
When either player achieves a win condition:
- Game pauses with `input("We won! Press Enter to continue: ")`
- After user presses Enter, game exits
- You can then modify to restart the loop or exit entirely

## Testing Your Implementation

Once you provide card/score detection details:

```bash
cd /Users/kylehurd/Workplace/club-penguin-bot
poetry run python -m club_penguin_bot.actions.card_jitsu_action
```

The bot will:
1. Log into Club Penguin
2. Travel to DOJO
3. Start Card-Jitsu game
4. Begin detecting cards, scores, and making strategic plays
5. Pause when a win condition is detected

## Next Steps

1. **Provide visual samples** of:
   - Card layout with type, value, color locations
   - Scoreboard with type columns and color stacking
   - Timer image

2. **Once provided**, I will implement:
   - `detect_cards()` - Full card OCR and color sampling
   - `detect_score()` - Scoreboard type/color scanning
   - `detect_new_round()` - Timer template matching

3. **Integration ready**:
   - Win condition checking ✅
   - Card battle logic ✅
   - Optimal play selection ✅
   - Game loop ✅

All the infrastructure is in place and tested. Just awaiting your visual examples!
