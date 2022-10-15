# Loot History

This is a small data visualisation program for tracking the distribution of rewards in guilds in the game World of Warcraft (Classic specifically, no promises for Retail).

Intended for use by Loot Council's to enable some kind of data tracking over time, due to the randomised nature of team rewards from raiding.

Loot History uses Matplotlib for its plotting capabilities, and will produce a team plot showing all members and their reward totals alongside each other, as well as individual plots per player showing their accrued loot over time. The images produced are .png and easily shareable via Discord or whatever other communication platform your team uses.

Using this tool in concert with the popular site ThatsMyBis is advised, as it allows some management of active / inactive team members without directly touching the datasets. Simply export your data from your preferred in game addon (RCLootCouncil etc), and upload to ThatsMyBis. Specific instructions regarding export and upload are available on ThatsMyBis itself. The JSON data made available for download via ThatsMyBis ensures only players marked as active in the team are included in the final plots, as well as allowing datasets for multiple teams to be parsed via the associated team names.

Plots are also bounded by date, so if you want to see the history across multiple phases, simply choose the starting date that corresponds to a particular patch release date to generate plots with all data from that date until today.






