(function () {
  "use strict";

  /* ----------------------------------------------------------- elements */

  const searchForm = document.getElementById("searchForm");
  const nameInput = document.getElementById("nameInput");
  const regionSelect = document.getElementById("region");
  const searchButton = document.getElementById("searchButton");

  const statusEl = document.getElementById("status");
  const playerContainer = document.getElementById("player-container");
  const profileContainer = document.getElementById("profile-container");
  const dataContainer = document.getElementById("data-container");
  const showMoreDiv = document.getElementById("showMoreButtonDiv");

  const state = {
    searchToken: 0,
    cards: [],
    rankCache: {},
    riotID: "",
    busy: false,
  };

  const RANK_ICONS = new Set([
    "iron",
    "bronze",
    "silver",
    "gold",
    "platinum",
    "emerald",
    "diamond",
    "master",
    "grandmaster",
    "challenger",
  ]);

  const APEX_TIERS = new Set(["MASTER", "GRANDMASTER", "CHALLENGER"]);
  const TIER_ORDER = [
    "IRON",
    "BRONZE",
    "SILVER",
    "GOLD",
    "PLATINUM",
    "EMERALD",
    "DIAMOND",
    "MASTER",
    "GRANDMASTER",
    "CHALLENGER",
  ];
  const TIER_SCORE = {
    IRON: 0,
    BRONZE: 4,
    SILVER: 8,
    GOLD: 12,
    PLATINUM: 16,
    EMERALD: 20,
    DIAMOND: 24,
    MASTER: 28,
    GRANDMASTER: 32,
    CHALLENGER: 36,
  };
  const DIVISION_LABEL = ["IV", "III", "II", "I"];
  const ITEM_SLOTS = ["item0", "item1", "item2", "item3", "item4", "item5", "item6"];
  const CHAMP_CLASS_RE = /^[A-Za-z_][A-Za-z0-9_-]*$/;

  /* ------------------------------------------------------------ helpers */

  function escapeHtml(value) {
    return String(value == null ? "" : value).replace(/[&<>"']/g, function (char) {
      return {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      }[char];
    });
  }

  function setStatus(message, tone) {
    statusEl.textContent = message || "";
    statusEl.classList.toggle("is-error", tone === "error");
    statusEl.classList.toggle("is-ok", tone === "ok");
  }

  function setBusy(isBusy) {
    state.busy = isBusy;
    searchButton.disabled = isBusy;
    searchButton.setAttribute("aria-busy", String(isBusy));
    searchButton.textContent = isBusy ? "Searching…" : "Track";
  }

  function showEmpty(message) {
    dataContainer.innerHTML =
      '<div class="empty-state"><p>' + escapeHtml(message) + "</p></div>";
  }

  function showSkeletons() {
    dataContainer.innerHTML = new Array(4).fill('<div class="skeleton-card"></div>').join("");
  }

  function clearResults() {
    dataContainer.innerHTML = "";
    showMoreDiv.innerHTML = "";
    profileContainer.hidden = true;
    profileContainer.innerHTML = "";
    playerContainer.hidden = true;
    playerContainer.innerHTML = "";
  }

  async function postJSON(url, body) {
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    const text = await response.text();
    let data = null;
    if (text) {
      try {
        data = JSON.parse(text);
      } catch (error) {
        data = null;
      }
    }

    if (!response.ok) {
      throw new Error((data && data.error) || "Request failed (" + response.status + ").");
    }
    if (data && data.error) {
      throw new Error(data.error);
    }
    return data;
  }

  function formatDate(value) {
    const match = /^(\d{4})-(\d{2})-(\d{2})/.exec(String(value || ""));
    if (!match) {
      return value || "";
    }
    const date = new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]));
    const options =
      date.getFullYear() === new Date().getFullYear()
        ? { month: "short", day: "numeric" }
        : { month: "short", day: "numeric", year: "numeric" };
    return date.toLocaleDateString(undefined, options);
  }

  function durationToMinutes(value) {
    const parts = String(value || "0:00").split(":");
    const minutes = Number(parts[0]) || 0;
    const seconds = Number(parts[1]) || 0;
    return minutes + seconds / 60;
  }

  function kdaRatio(kills, deaths, assists) {
    const k = Number(kills) || 0;
    const d = Number(deaths) || 0;
    const a = Number(assists) || 0;
    if (d === 0) {
      return k + a > 0 ? "∞" : "0.00";
    }
    return ((k + a) / d).toFixed(2);
  }

  function killParticipation(player, participants) {
    const teamId = player.playerTeamID;
    const teamKills = participants.reduce(function (total, member) {
      if (teamId != null && member.playerTeamID !== teamId) {
        return total;
      }
      return total + (Number(member.kills) || 0);
    }, 0);

    if (!teamKills) {
      return 0;
    }
    const involved = (Number(player.kills) || 0) + (Number(player.assists) || 0);
    return Math.round((involved / teamKills) * 100);
  }

  function formatNumber(value) {
    const number = Number(value);
    return Number.isFinite(number) ? number.toLocaleString("en-US") : "—";
  }

  /* --------------------------------------------------------------- ranks */

  function tierLabel(tier) {
    const value = String(tier || "");
    return value ? value.charAt(0) + value.slice(1).toLowerCase() : "";
  }

  function formatRank(rank) {
    if (!rank) {
      return "—";
    }

    const tier = String(rank.tier || "").toUpperCase();
    if (!tier || tier === "UNRANKED") {
      return "Unranked";
    }

    const label = tierLabel(tier);
    const lp = Math.max(0, Number(rank.leaguePoints) || 0);

    if (APEX_TIERS.has(tier)) {
      return label + " · " + lp + " LP";
    }

    const division = String(rank.rank || "").toUpperCase();
    return label + (division ? " " + division : "") + " · " + lp + " LP";
  }

  function rankScore(rank) {
    if (!rank) {
      return null;
    }

    const tier = String(rank.tier || "").toUpperCase();
    const base = TIER_SCORE[tier];
    if (base == null || tier === "UNRANKED") {
      return null;
    }

    const lp = Math.max(0, Number(rank.leaguePoints) || 0);

    if (APEX_TIERS.has(tier)) {
      return base + Math.min(lp, 9000) / 100;
    }

    const division = DIVISION_LABEL.indexOf(String(rank.rank || "").toUpperCase());
    return base + (division < 0 ? 0 : division) + Math.min(lp, 100) / 100;
  }

  function formatAverageScore(average) {
    const tierIndex = Math.max(0, Math.min(TIER_ORDER.length - 1, Math.floor(average / 4)));
    const tier = TIER_ORDER[tierIndex];
    const label = tierLabel(tier);

    if (tierIndex >= 7) {
      return label + " · " + Math.max(0, Math.round((average - TIER_SCORE[tier]) * 100)) + " LP";
    }

    const within = Math.max(0, Math.min(3.999, average - tierIndex * 4));
    const divisionIndex = Math.min(3, Math.floor(within));
    return label + " " + DIVISION_LABEL[divisionIndex];
  }

  function rankFor(member) {
    if (member && member.puuid && Object.prototype.hasOwnProperty.call(state.rankCache, member.puuid)) {
      return state.rankCache[member.puuid];
    }
    return (member && member.rank) || null;
  }

  function lobbyRanksKnown(record) {
    const participants = (record && record.participants) || [];
    if (!participants.length) {
      return false;
    }
    return participants.every(function (participant) {
      return Boolean(rankFor(participant));
    });
  }

  function averageRankLabel(record) {
    // Show the average straight away when every rank is already available
    // (cached from an earlier visit or attached from the database). Only ask
    // the user to expand when some ranks still need to be fetched.
    if (!record) {
      return "Lobby avg: click";
    }

    const known = record.ranksLoaded || lobbyRanksKnown(record);
    if (!known) {
      return record.expanded ? "Loading avg…" : "Lobby avg: click";
    }

    const participants = record.participants || [];
    const scores = [];
    let unranked = 0;

    participants.forEach(function (participant) {
      const rank = rankFor(participant);
      const score = rankScore(rank);
      if (score == null) {
        if (rank) {
          unranked += 1;
        }
        return;
      }
      scores.push(score);
    });

    if (!scores.length) {
      return unranked ? "Unranked lobby" : "Avg —";
    }

    const average = scores.reduce(function (total, score) {
      return total + score;
    }, 0) / scores.length;

    return "Avg " + formatAverageScore(average);
  }

  function rememberRank(puuid, rank) {
    if (puuid && rank) {
      state.rankCache[puuid] = rank;
    }
  }

  function applyRankLabels() {
    dataContainer.querySelectorAll("[data-rank-puuid]").forEach(function (element) {
      const puuid = element.getAttribute("data-rank-puuid");
      const rank = puuid ? state.rankCache[puuid] || null : null;
      const tier = rank ? String(rank.tier || "").toUpperCase() : "";
      element.textContent = formatRank(rank);
      element.classList.toggle("is-unranked", tier === "UNRANKED");
      element.classList.toggle("is-unknown", !rank);
    });
  }

  function refreshAverages() {
    state.cards.forEach(function (record, index) {
      const element = dataContainer.querySelector('[data-avg-index="' + index + '"]');
      if (element) {
        element.textContent = averageRankLabel(record);
      }
    });
  }

  /* ------------------------------------------------------------ sprites */

  // Riot's Match API returns "FiddleSticks" while the sprite sheets use
  // "Fiddlesticks". Keep that one API naming quirk out of the markup.
  const SPRITE_ALIASES = {
    fiddlesticks: "Fiddlesticks",
  };

  // Sprite classes are generated from display names, so apply the same
  // sanitisation the stylesheet uses ("B. F. Sword" -> "B-F-Sword",
  // "Jak'Sho, The Protean" -> "Jak_Sho_-The-Protean").
  function spriteClass(name) {
    const raw = String(name == null ? "" : name);
    const alias = SPRITE_ALIASES[raw.toLowerCase()];
    if (alias) {
      return alias;
    }
    return raw
      .replace(/\./g, "")
      .replace(/[':,()]/g, "_")
      .replace(/\s+/g, "-");
  }

  function sprite(kind, name, extraClass) {
    const raw = name == null ? "" : String(name);
    const className = spriteClass(raw);
    const valid = CHAMP_CLASS_RE.test(className);
    const classes = ["sprite", kind];

    if (extraClass) {
      classes.push(extraClass);
    }

    if (!valid || /^(PlaceholderItem|Placeholder|Not Found)$/i.test(raw)) {
      return '<span class="' + classes.join(" ") + ' sprite-empty" aria-hidden="true"></span>';
    }

    classes.push(className);
    const label = escapeHtml(SPRITE_ALIASES[raw.toLowerCase()] || raw);
    return (
      '<span class="' +
      classes.join(" ") +
      '" role="img" aria-label="' +
      label +
      '" title="' +
      label +
      '"></span>'
    );
  }

  function itemSprites(player) {
    return ITEM_SLOTS.map(function (slot) {
      return sprite("item", player[slot]);
    }).join("");
  }

  function cardItems(player) {
    return (
      '<span class="item-grid">' +
      ITEM_SLOTS.slice(0, 6)
        .map(function (slot) {
          return sprite("item", player[slot]);
        })
        .join("") +
      "</span>" +
      '<span class="item-trinket">' +
      sprite("item", player.item6) +
      "</span>"
    );
  }

  /* ------------------------------------------------------------ rune page */

  function runeIconUrl(icon) {
    if (!icon) {
      return "";
    }
    return (
      "/getRuneIcons/" +
      String(icon)
        .split("/")
        .map(function (part) {
          return encodeURIComponent(part);
        })
        .join("/")
    );
  }

  function runeItem(rune, isKeystone) {
    if (!rune) {
      return "";
    }

    const name = escapeHtml(rune.name || "");
    const icon = rune.icon
      ? '<img src="' +
        escapeHtml(runeIconUrl(rune.icon)) +
        '" alt="" width="24" height="24" loading="lazy" />'
      : '<span class="rune-fallback" aria-hidden="true">?</span>';

    return (
      '<span class="rune-item' +
      (isKeystone ? " is-keystone" : "") +
      '" title="' +
      name +
      '">' +
      icon +
      '<span class="rune-name">' +
      name +
      "</span>" +
      "</span>"
    );
  }

  function runeStyleBlock(label, style, isPrimary) {
    if (!style) {
      return "";
    }

    const treeIcon = style.icon
      ? '<img class="rune-tree-icon" src="' +
        escapeHtml(runeIconUrl(style.icon)) +
        '" alt="" width="20" height="20" loading="lazy" />'
      : "";

    const runes = (style.runes || [])
      .map(function (rune, index) {
        return runeItem(rune, isPrimary && index === 0);
      })
      .join("");

    return (
      '<div class="rune-branch">' +
      '<div class="rune-branch-head">' +
      treeIcon +
      "<span>" +
      escapeHtml(label) +
      "</span>" +
      (style.name ? "<strong>" + escapeHtml(style.name) + "</strong>" : "") +
      "</div>" +
      '<div class="rune-list">' +
      runes +
      "</div>" +
      "</div>"
    );
  }

  function runePageHtml(page) {
    if (!page || !page.primary) {
      return (
        '<div class="rune-page is-empty">' +
        "<p>Full rune page is not stored for this older match.</p>" +
        '<p class="muted">Reopen the match to fetch the missing data from Riot.</p>' +
        "</div>"
      );
    }

    const shards = (page.shards || [])
      .map(function (shard) {
        return runeItem(shard, false);
      })
      .join("");

    return (
      '<div class="rune-page">' +
      runeStyleBlock("Primary", page.primary, true) +
      runeStyleBlock("Secondary", page.secondary, false) +
      (shards
        ? '<div class="rune-branch rune-shards">' +
          '<div class="rune-branch-head"><span>Stat shards</span></div>' +
          '<div class="rune-list">' +
          shards +
          "</div>" +
          "</div>"
        : "") +
      "</div>"
    );
  }

  function runeIconImage(icon, className, size) {
    if (!icon) {
      return "";
    }
    return (
      '<img class="' +
      className +
      '" src="' +
      escapeHtml(runeIconUrl(icon)) +
      '" alt="" width="' +
      size +
      '" height="' +
      size +
      '" loading="lazy" />'
    );
  }

  // Legacy keystones such as Deathfire Touch are missing from the bundled
  // sprite sheets, so prefer the real icon stored with the rune page.
  function keystoneMarkup(member, className, size) {
    const primary = member && member.runePage && member.runePage.primary;
    const rune = primary && primary.runes && primary.runes[0];
    if (rune && rune.icon) {
      return runeIconImage(rune.icon, className, size);
    }
    return sprite("rune", member && member.keystone);
  }

  function secondaryTreeMarkup(member, className, size) {
    const secondary = member && member.runePage && member.runePage.secondary;
    if (secondary && secondary.icon) {
      return runeIconImage(secondary.icon, className, size);
    }
    return sprite("runecat", member && member.secondaryRune);
  }

  function runeToggle(member) {
    if (!member.runePage) {
      return '<span class="rune-missing" title="Rune page unavailable">—</span>';
    }

    return (
      '<button class="rune-toggle" type="button" aria-expanded="false" aria-label="Show full rune page for ' +
      escapeHtml(member.riotID) +
      '">' +
      keystoneMarkup(member, "rune-toggle-icon", 20) +
      secondaryTreeMarkup(member, "rune-toggle-tree", 16) +
      '<span class="rune-caret" aria-hidden="true"></span>' +
      "</button>"
    );
  }

  /* --------------------------------------------------------- rank card */

  function renderRank(payload) {
    const data = Array.isArray(payload) ? payload[0] : payload;
    if (!data) {
      renderUnranked("No Ranked Solo/Duo data for this player.");
      return;
    }

    const tier = String(data.tier || "").toUpperCase();
    const division = String(data.rank || "").toUpperCase();
    const lp = Math.max(0, Math.min(100, Number(data.leaguePoints) || 0));
    const wins = Number(data.wins) || 0;
    const losses = Number(data.losses) || 0;
    const total = wins + losses;
    const winRate = total ? Math.round((wins / total) * 100) : 0;

    const tierName = tier
      ? tier.charAt(0) + tier.slice(1).toLowerCase()
      : "Unranked";
    const showDivision = tier && division && !APEX_TIERS.has(tier);

    let emblem;
    if (RANK_ICONS.has(tier.toLowerCase())) {
      emblem =
        '<img class="rank-emblem" src="/static/img/rankIcons/' +
        tier.toLowerCase() +
        '.webp" alt="" width="68" height="68" />';
    } else {
      emblem =
        '<span class="rank-emblem rank-emblem--fallback" aria-hidden="true">' +
        escapeHtml(tierName.charAt(0) || "?") +
        "</span>";
    }

    playerContainer.innerHTML =
      '<div class="rank-card">' +
      emblem +
      '<div class="rank-body">' +
      '<p class="eyebrow">Ranked Solo/Duo</p>' +
      '<p class="rank-tier">' +
      escapeHtml(tierName) +
      (showDivision ? ' <span class="division">' + escapeHtml(division) + "</span>" : "") +
      "</p>" +
      '<div class="lp-meter" role="img" aria-label="' +
      lp +
      ' league points"><span style="width:' +
      lp +
      '%"></span></div>' +
      '<p class="rank-meta">' +
      "<span><strong>" +
      lp +
      "</strong> LP</span>" +
      "<span><strong>" +
      wins +
      "</strong>W <strong>" +
      losses +
      "</strong>L</span>" +
      '<span class="win-rate">' +
      winRate +
      "% WR</span>" +
      "</p>" +
      "</div>" +
      "</div>";
    playerContainer.hidden = false;
  }

  function renderUnranked(message) {
    playerContainer.innerHTML =
      '<div class="rank-card">' +
      '<span class="rank-emblem rank-emblem--fallback" aria-hidden="true">?</span>' +
      '<div class="rank-body">' +
      '<p class="eyebrow">Ranked Solo/Duo</p>' +
      '<p class="rank-tier">Unranked</p>' +
      '<p class="rank-meta">' +
      escapeHtml(message || "No Ranked Solo/Duo data for this player.") +
      "</p>" +
      "</div>" +
      "</div>";
    playerContainer.hidden = false;
  }

  async function rankSearch(riotID, token) {
    try {
      const data = await postJSON("/getRank", {
        riotID: riotID,
        regionSelect: regionSelect.value,
      });
      if (token != null && token !== state.searchToken) {
        return;
      }
      renderRank(data);
    } catch (error) {
      if (token != null && token !== state.searchToken) {
        return;
      }
      renderUnranked(error.message);
    }
  }

  /* ------------------------------------------------------------ profile */

  function renderProfile(riotID, count) {
    profileContainer.innerHTML =
      '<div class="profile">' +
      "<div>" +
      '<p class="eyebrow">Match history</p>' +
      "<h1>" +
      escapeHtml(riotID) +
      "</h1>" +
      "</div>" +
      '<div class="profile-actions">' +
      '<span class="game-count">' +
      count +
      (count === 1 ? " game" : " games") +
      "</span>" +
      '<button class="btn btn-ghost" type="button" data-action="update">Refresh</button>' +
      "</div>" +
      "</div>";
    profileContainer.hidden = false;
  }

  /* -------------------------------------------------------- match cards */

  function teamRoster(team, player, label, isEnemy) {
    if (!team.length) {
      return "";
    }

    const champs = team
      .slice(0, 5)
      .map(function (member) {
        const isYou =
          member.riotID &&
          player.riotID &&
          member.riotID.toLowerCase() === player.riotID.toLowerCase();
        return sprite(
          "champ",
          member.Champ,
          "team-champ" + (isYou ? " is-you" : "")
        );
      })
      .join("");

    return (
      '<span class="team-row' +
      (isEnemy ? " is-enemy" : "") +
      '" title="' +
      label +
      '">' +
      champs +
      "</span>"
    );
  }

  function teamRosters(player, participants) {
    if (!participants || !participants.length) {
      return "";
    }

    const teamId = player.playerTeamID;
    const own = participants.filter(function (member) {
      return teamId != null
        ? member.playerTeamID === teamId
        : Boolean(member.win) === Boolean(player.win);
    });
    const ownIds = new Set(own);
    const enemy = participants.filter(function (member) {
      return !ownIds.has(member);
    });

    return (
      '<span class="team-rosters" aria-label="Team champions">' +
      teamRoster(own, player, "Your team", false) +
      teamRoster(enemy, player, "Enemy team", true) +
      "</span>"
    );
  }

  function buildMatchCard(game, player, participants, index) {
    const win = Boolean(player.win);
    const kills = Number(player.kills) || 0;
    const deaths = Number(player.deaths) || 0;
    const assists = Number(player.assists) || 0;
    const ratio = kdaRatio(kills, deaths, assists);
    const minutes = durationToMinutes(game.gameDurationMinutes);
    const csPerMin = minutes > 0 ? ((Number(player.totalCS) || 0) / minutes).toFixed(1) : "0.0";
    const totalGold = Number(player.goldEarned) || 0;
    const goldPerMin = minutes > 0 ? Math.round(totalGold / minutes) : 0;
    const participation = killParticipation(player, participants);
    const gameID = game.gameID || "";

    return (
      '<details class="match-card ' +
      (win ? "is-win" : "is-loss") +
      '" data-index="' +
      index +
      '" data-game-id="' +
      escapeHtml(gameID) +
      '">' +
      '<summary class="match-summary">' +
      '<span class="result-rail" aria-hidden="true"></span>' +
      '<span class="match-outcome">' +
      '<span class="outcome-label">' +
      (win ? "Victory" : "Defeat") +
      "</span>" +
      '<span class="outcome-sub">' +
      escapeHtml(game.gameDurationMinutes || "") +
      "</span>" +
      '<span class="outcome-sub">' +
      escapeHtml(formatDate(game.gameDate)) +
      "</span>" +
      '<span class="outcome-sub lobby-avg" data-avg-index="' +
      index +
      '" title="Expand this match to see the full scoreboard and rank details.">' +
      escapeHtml(averageRankLabel(state.cards[index])) +
      "</span>" +
      "</span>" +
      '<span class="champion">' +
      '<span class="champ-wrap">' +
      sprite("champ", player.Champ) +
      '<span class="level-badge">' +
      escapeHtml(player.champLevel) +
      "</span>" +
      "</span>" +
      '<span class="spells">' +
      sprite("spell", player.summonerSpell1) +
      sprite("spell", player.summonerSpell2) +
      "</span>" +
      "</span>" +
      '<span class="runes">' +
      keystoneMarkup(player, "rune-summary-icon", 26) +
      secondaryTreeMarkup(player, "rune-summary-tree", 20) +
      "</span>" +
      '<span class="items">' +
      cardItems(player) +
      "</span>" +
      teamRosters(player, participants) +
      '<span class="kda-block">' +
      '<span class="kda">' +
      kills +
      ' / <span class="deaths">' +
      deaths +
      "</span> / " +
      assists +
      "</span>" +
      '<span class="kda-ratio">' +
      ratio +
      " KDA</span>" +
      "</span>" +
      '<span class="stats">' +
      '<span class="stat"><b>' +
      participation +
      "%</b><small>KP</small></span>" +
      '<span class="stat"><b>' +
      csPerMin +
      "</b><small>CS/min</small></span>" +
      '<span class="stat"><b>' +
      formatNumber(totalGold) +
      "</b><small>Gold</small></span>" +
      '<span class="stat"><b>' +
      formatNumber(goldPerMin) +
      "</b><small>Gold/min</small></span>" +
      "</span>" +
      '<span class="chevron" aria-hidden="true"></span>' +
      "</summary>" +
      '<div class="match-details" data-loaded="false"></div>' +
      "</details>"
    );
  }

  function buildScoreTable(team, profileName) {
    const rows = team
      .map(function (member) {
        const isYou =
          member.riotID &&
          profileName &&
          member.riotID.toLowerCase() === profileName.toLowerCase();
        const level = escapeHtml(member.champLevel);
        const name = escapeHtml(member.riotID);
        const puuid = member.puuid || "";
        const rank = rankFor(member);
        const rankTier = rank ? String(rank.tier || "").toUpperCase() : "";
        const rankClass = !rank ? " is-unknown" : rankTier === "UNRANKED" ? " is-unranked" : "";
        const rankAttribute = puuid
          ? ' data-rank-puuid="' + escapeHtml(puuid) + '"'
          : "";

        return (
          '<tr class="' +
          (isYou ? "is-you" : "") +
          '">' +
          "<td>" +
          '<span class="score-champ">' +
          '<span class="champ-wrap">' +
          sprite("champ", member.Champ, "champ-sm") +
          '<span class="level-badge">' +
          level +
          "</span>" +
          "</span>" +
          '<span class="spells">' +
          sprite("spell", member.summonerSpell1) +
          sprite("spell", member.summonerSpell2) +
          "</span>" +
          "</span>" +
          "</td>" +
          '<td class="player-cell">' +
          '<button class="player-link" type="button" data-riot-id="' +
          name +
          '" title="View ' +
          name +
          '">' +
          name +
          "</button>" +
          '<span class="player-rank' +
          rankClass +
          '"' +
          rankAttribute +
          ">" +
          escapeHtml(formatRank(rank)) +
          "</span>" +
          "</td>" +
          "<td>" +
          (Number(member.kills) || 0) +
          " / " +
          (Number(member.deaths) || 0) +
          " / " +
          (Number(member.assists) || 0) +
          "</td>" +
          "<td>" +
          formatNumber(member.goldEarned) +
          "</td>" +
          "<td>" +
          (Number(member.totalCS) || 0) +
          "</td>" +
          '<td class="rune-cell">' +
          runeToggle(member) +
          "</td>" +
          '<td><span class="item-cell">' +
          itemSprites(member) +
          "</span></td>" +
          "</tr>" +
          '<tr class="rune-page-row" hidden><td colspan="7">' +
          runePageHtml(member.runePage) +
          "</td></tr>"
        );
      })
      .join("");

    return (
      '<div class="table-scroll">' +
      '<table class="score-table">' +
      "<thead><tr>" +
      '<th scope="col">Champion</th>' +
      '<th scope="col">Player</th>' +
      '<th scope="col">KDA</th>' +
      '<th scope="col">Gold</th>' +
      '<th scope="col">CS</th>' +
      '<th scope="col">Runes</th>' +
      '<th scope="col">Items</th>' +
      "</tr></thead>" +
      "<tbody>" +
      rows +
      "</tbody>" +
      "</table>" +
      "</div>"
    );
  }

  function buildDetails(record) {
    const player = record.player;
    const participants = record.participants || [];
    const teamId = player.playerTeamID;

    const own = participants.filter(function (member) {
      return teamId != null
        ? member.playerTeamID === teamId
        : Boolean(member.win) === Boolean(player.win);
    });
    const ownIds = new Set(own);
    const enemy = participants.filter(function (member) {
      return !ownIds.has(member);
    });

    return (
      '<div class="team-block">' +
      '<h3 class="team-heading">Your Team</h3>' +
      buildScoreTable(own, player.riotID) +
      "</div>" +
      '<div class="team-block enemy">' +
      '<h3 class="team-heading">Enemy Team</h3>' +
      buildScoreTable(enemy, player.riotID) +
      "</div>" +
      '<p class="rank-note" data-rank-note hidden></p>'
    );
  }

  function renderMatches(data, append) {
    const games = Array.isArray(data.gameData) ? data.gameData : [];
    const players = Array.isArray(data.playerStats) ? data.playerStats : [];
    const matchData = Array.isArray(data.matchData) ? data.matchData : [];

    const html = [];

    games.forEach(function (game, index) {
      const player = players[index];
      const participants = matchData[index];

      // A Riot ID change can leave a stored match without a player-stat row.
      // Skip that card rather than rendering an empty one.
      if (!player || !Array.isArray(participants)) {
        return;
      }

      participants.forEach(function (participant) {
        if (participant && participant.puuid && participant.rank) {
          rememberRank(participant.puuid, participant.rank);
        }
      });

      const cardIndex = state.cards.length;
      state.cards.push({
        game: game,
        player: player,
        participants: participants,
        expanded: false,
        ranksLoaded: false,
      });
      html.push(buildMatchCard(game, player, participants, cardIndex));
    });

    if (append) {
      dataContainer.insertAdjacentHTML("beforeend", html.join(""));
    } else {
      dataContainer.innerHTML = html.join("");
    }

    renderProfile(state.riotID, state.cards.length);
    refreshAverages();
    return html.length;
  }

  function renderShowMore() {
    showMoreDiv.innerHTML =
      '<button id="showMoreButtonTag" class="btn btn-ghost" type="button">Show more</button>';
  }

  /* ------------------------------------------------ lazy ranks / rune pages */

  async function loadLobbyRanks(record, details) {
    if (!record || record.ranksLoading || record.ranksLoaded) {
      return;
    }

    const needsRank = record.participants.some(function (participant) {
      return participant && participant.puuid && !rankFor(participant);
    });
    if (!needsRank) {
      record.ranksLoaded = true;
      refreshAverages();
      return;
    }

    record.ranksLoading = true;
    const players = record.participants
      .filter(function (participant) {
        return participant && (participant.puuid || participant.riotID);
      })
      .map(function (participant) {
        return {
          riotID: participant.riotID || "",
          puuid: participant.puuid || "",
        };
      });

    try {
      const data = await postJSON("/getLobbyRanks", {
        players: players,
        regionSelect: regionSelect.value,
        fetchMissing: true,
      });

      const ranks = (data && data.ranks) || {};
      Object.keys(ranks).forEach(function (puuid) {
        const rank = ranks[puuid];
        if (!rank) {
          return;
        }
        state.rankCache[puuid] = rank;
        state.cards.forEach(function (card) {
          (card.participants || []).forEach(function (participant) {
            if (participant && participant.puuid === puuid) {
              participant.rank = rank;
            }
          });
        });
      });

      applyRankLabels();

      if (data && data.rateLimited && details) {
        const note = details.querySelector("[data-rank-note]");
        if (note) {
          note.textContent = "Riot rate limit reached — some ranks could not be loaded.";
          note.hidden = false;
        }
      }
    } catch (error) {
      // Ranks are progressive enhancement; the scoreboard still works without them.
    } finally {
      record.ranksLoading = false;
      record.ranksLoaded = true;
      refreshAverages();
    }
  }

  async function loadMatchRunes(record, details) {
    if (!record || record.runesLoading || record.runesLoaded) {
      return;
    }

    const needsRunes = record.participants.some(function (participant) {
      return participant && participant.puuid && !participant.runePage;
    });
    if (!needsRunes) {
      record.runesLoaded = true;
      return;
    }

    record.runesLoading = true;
    try {
      const data = await postJSON("/getMatchRunes", {
        gameID: record.game.gameID,
        regionSelect: regionSelect.value,
      });
      const pages = (data && data.runePages) || {};
      let changed = false;

      state.cards.forEach(function (card) {
        (card.participants || []).forEach(function (participant) {
          if (participant && participant.puuid && pages[participant.puuid]) {
            participant.runePage = pages[participant.puuid];
            changed = true;
          }
        });
      });

      if (changed && details && details.open) {
        const body = details.querySelector(".match-details");
        if (body) {
          body.innerHTML = buildDetails(record);
          body.dataset.loaded = "true";
        }
      }
    } catch (error) {
      // Older matches may fall outside Riot's retention window.
    } finally {
      record.runesLoading = false;
      record.runesLoaded = true;
    }
  }

  /* -------------------------------------------------------------- search */

  async function summonerSearch() {
    const name = nameInput.value.trim();

    if (!name) {
      setStatus("Enter a Riot ID to search.", "error");
      nameInput.focus();
      return;
    }
    if (name.indexOf("#") === -1) {
      setStatus("Enter your Riot ID as Game Name#Tagline.", "error");
      nameInput.focus();
      return;
    }

    const token = ++state.searchToken;
    state.riotID = name;
    state.cards = [];

    setStatus("Searching for summoner…");
    setBusy(true);
    clearResults();
    showSkeletons();

    try {
      const data = await postJSON("/summonerSearch", {
        summonerName: name,
        regionSelect: regionSelect.value,
      });

      if (token !== state.searchToken) {
        return;
      }

      state.riotID = data.riotID || name;

      if (!Array.isArray(data.gameData) || data.gameData.length === 0) {
        showEmpty("No recent Ranked Solo/Duo matches were returned for this player.");
        setStatus("");
        return;
      }

      renderMatches(data, false);
      if (data.gameData.length >= 20) {
        renderShowMore();
      }
      setStatus("");
      rankSearch(state.riotID, token);
    } catch (error) {
      if (token !== state.searchToken) {
        return;
      }
      showEmpty("Could not load match history. Check the Riot ID and region, then try again.");
      setStatus(error.message || "Search failed.", "error");
    } finally {
      if (token === state.searchToken) {
        setBusy(false);
      }
    }
  }

  async function showMore() {
    const button = showMoreDiv.querySelector("button");
    const name = state.riotID || nameInput.value.trim();

    if (!button || button.disabled || !name) {
      return;
    }

    const excludeGameIDs = Array.from(
      dataContainer.querySelectorAll("[data-game-id]")
    )
      .map(function (element) {
        return element.getAttribute("data-game-id");
      })
      .filter(Boolean);

    button.disabled = true;
    button.textContent = "Loading…";
    setStatus("Loading more games…");

    try {
      const data = await postJSON("/showMore", {
        searchedUser: name,
        excludeGameIDs: excludeGameIDs,
        regionSelect: regionSelect.value,
      });

      const rendered = renderMatches(data, true);

      if (rendered === 0) {
        showMoreDiv.innerHTML = '<span class="muted">No more games.</span>';
      } else {
        renderShowMore();
      }
      setStatus("");
    } catch (error) {
      setStatus(error.message || "Could not load more games.", "error");
      button.disabled = false;
      button.textContent = "Show more";
    }
  }

  async function updateData() {
    const name = state.riotID || nameInput.value.trim();

    if (!name || state.busy) {
      return;
    }

    const token = ++state.searchToken;
    state.cards = [];

    setStatus("Refreshing match history…");
    const refreshButton = profileContainer.querySelector('[data-action="update"]');
    if (refreshButton) {
      refreshButton.disabled = true;
      refreshButton.textContent = "Refreshing…";
    }

    try {
      const data = await postJSON("/getHistory", {
        riotID: name,
        regionSelect: regionSelect.value,
      });

      if (token !== state.searchToken) {
        return;
      }

      if (!Array.isArray(data.gameData) || data.gameData.length === 0) {
        clearResults();
        showEmpty("No recent Ranked Solo/Duo matches were returned for this player.");
        setStatus("");
        return;
      }

      dataContainer.innerHTML = "";
      showMoreDiv.innerHTML = "";
      renderMatches(data, false);
      if (data.gameData.length >= 20) {
        renderShowMore();
      }
      setStatus("Updated.", "ok");
      rankSearch(name, token);
    } catch (error) {
      if (token !== state.searchToken) {
        return;
      }
      setStatus(error.message || "Refresh failed.", "error");
      if (refreshButton) {
        refreshButton.disabled = false;
        refreshButton.textContent = "Refresh";
      }
    }
  }

  /* ------------------------------------------------------------- events */

  searchForm.addEventListener("submit", function (event) {
    event.preventDefault();
    summonerSearch();
  });

  dataContainer.addEventListener(
    "toggle",
    function (event) {
      const details = event.target;
      if (!details || !details.open) {
        return;
      }
      const body = details.querySelector(".match-details");
      const record = state.cards[Number(details.dataset.index)];
      if (!body || !record) {
        return;
      }

      if (body.dataset.loaded !== "true") {
        body.innerHTML = buildDetails(record);
        body.dataset.loaded = "true";
      }

      record.expanded = true;
      refreshAverages();

      loadMatchRunes(record, details);
      loadLobbyRanks(record, details);
    },
    true
  );

  dataContainer.addEventListener("click", function (event) {
    const playerLink = event.target.closest(".player-link");
    if (playerLink) {
      const riotID = playerLink.getAttribute("data-riot-id");
      if (riotID) {
        event.preventDefault();
        event.stopPropagation();
        nameInput.value = riotID;
        summonerSearch();
        window.scrollTo({ top: 0, behavior: "smooth" });
      }
      return;
    }

    const toggle = event.target.closest(".rune-toggle");
    if (toggle) {
      event.preventDefault();
      const row = toggle.closest("tr");
      const pageRow = row && row.nextElementSibling;
      if (!pageRow || !pageRow.classList.contains("rune-page-row")) {
        return;
      }
      const opening = pageRow.hidden;
      pageRow.hidden = !opening;
      toggle.setAttribute("aria-expanded", String(opening));
    }
  });

  showMoreDiv.addEventListener("click", function (event) {
    if (event.target.closest("button")) {
      showMore();
    }
  });

  profileContainer.addEventListener("click", function (event) {
    if (event.target.closest('[data-action="update"]')) {
      updateData();
    }
  });
})();
