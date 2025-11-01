# Football Match Probability Predictor

Μια απλή εφαρμογή γραμμένη σε Python που διαβάζει ιστορικά δεδομένα αγώνων
ποδοσφαίρου από ένα αρχείο CSV και υπολογίζει πιθανότητες για διάφορα στοιχήματα
ενός επερχόμενου αγώνα: τελικό αποτέλεσμα (νίκη/ισοπαλία/ήττα), goal-goal,
αποτέλεσμα ημιχρόνου και over/under.

## Εγκατάσταση

Η εφαρμογή δεν έχει εξωτερικές εξαρτήσεις πέρα από την Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
```

## Δεδομένα

Το αρχείο CSV πρέπει να περιέχει τις στήλες:

- `date` (μορφή YYYY-MM-DD)
- `home_team`
- `away_team`
- `home_goals`
- `away_goals`
- `home_ht_goals`
- `away_ht_goals`
- `competition` (προαιρετικό)

Ένα δείγμα βρίσκεται στο `data/sample_matches.csv`.

## Χρήση

```bash
python -m football_predictor.cli data/sample_matches.csv "Team A" "Team B" --pretty
```

Παράδειγμα εξόδου:

```json
{
  "home_team": "Team A",
  "away_team": "Team B",
  "over_under_line": 2.5,
  "probabilities": {
    "home_win": {
      "value": 0.2857,
      "contributors": {
        "home_team": {
          "value": 0.5,
          "sample_size": 4
        },
        "away_team": {
          "value": 0.25,
          "sample_size": 4
        },
        "head_to_head": {
          "value": 0.1667,
          "sample_size": 6
        }
      }
    },
    "draw": {
      "value": 0.5,
      "contributors": {
        "home_team": {
          "value": 0.5,
          "sample_size": 4
        },
        "away_team": {
          "value": 0.5,
          "sample_size": 4
        },
        "head_to_head": {
          "value": 0.5,
          "sample_size": 6
        }
      }
    },
    "away_win": {
      "value": 0.2143,
      "contributors": {
        "home_team": {
          "value": 0.0,
          "sample_size": 4
        },
        "away_team": {
          "value": 0.25,
          "sample_size": 4
        },
        "head_to_head": {
          "value": 0.3333,
          "sample_size": 6
        }
      }
    },
    "goal_goal": {
      "value": 0.5714,
      "contributors": {
        "home_team": {
          "value": 0.5,
          "sample_size": 4
        },
        "away_team": {
          "value": 0.5,
          "sample_size": 4
        },
        "head_to_head": {
          "value": 0.6667,
          "sample_size": 6
        }
      }
    },
    "halftime_home_win": {
      "value": 0.2857,
      "contributors": {
        "home_team": {
          "value": 0.5,
          "sample_size": 4
        },
        "away_team": {
          "value": 0.25,
          "sample_size": 4
        },
        "head_to_head": {
          "value": 0.1667,
          "sample_size": 6
        }
      }
    },
    "halftime_draw": {
      "value": 0.2857,
      "contributors": {
        "home_team": {
          "value": 0.25,
          "sample_size": 4
        },
        "away_team": {
          "value": 0.25,
          "sample_size": 4
        },
        "head_to_head": {
          "value": 0.3333,
          "sample_size": 6
        }
      }
    },
    "halftime_away_win": {
      "value": 0.4286,
      "contributors": {
        "home_team": {
          "value": 0.25,
          "sample_size": 4
        },
        "away_team": {
          "value": 0.5,
          "sample_size": 4
        },
        "head_to_head": {
          "value": 0.5,
          "sample_size": 6
        }
      }
    },
    "over": {
      "value": 0.3571,
      "contributors": {
        "home_team": {
          "value": 0.5,
          "sample_size": 4
        },
        "away_team": {
          "value": 0.25,
          "sample_size": 4
        },
        "head_to_head": {
          "value": 0.3333,
          "sample_size": 6
        }
      }
    },
    "under": {
      "value": 0.6429,
      "contributors": {
        "home_team": {
          "value": 0.5,
          "sample_size": 4
        },
        "away_team": {
          "value": 0.75,
          "sample_size": 4
        },
        "head_to_head": {
          "value": 0.6667,
          "sample_size": 6
        }
      }
    }
  },
  "sample_sizes": {
    "home_matches": 4,
    "away_matches": 4,
    "head_to_head": 6
  }
}
```

Οι τιμές `contributors` δείχνουν την συμβολή κάθε πηγής δεδομένων (αγώνες της
γηπεδούχου, της φιλοξενούμενης και μεταξύ τους) μαζί με το πλήθος των αγώνων που
χρησιμοποιήθηκαν (`sample_size`). Το συνολικό `value` είναι ο σταθμισμένος μέσος
όρος αυτών των πιθανοτήτων με βάση τα διαθέσιμα δείγματα.
