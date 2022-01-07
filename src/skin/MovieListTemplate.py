# Copyright (C) 2018-2024 by dream-alpha
# pylint: skip-file
# flake8: noqa
#
# value indexes:
#  1: name
#  2: tags
#  3: service name
#  4: short description
#  5: date
#  6: length
#  7: color
#  8: color_sel
#  9: progress percent (-1 = don't show progress bar)
# 10: progress (xx%)
# 11: progress bar png
# 12: status icon png
# 13: picon png

{
	"list_styles": {
		#  identifier			, description					, row height,	, number of rows
		0: ("default"			, _("List style: default")			, 100		, 3),
		1: ("compact_description"	, _("List style: compact with description")	, 80		, 2),
		2: ("compact"			, _("List style: compact")			, 80		, 2),
		3: ("compact_single"		, _("List style: compact single line")		, 45		, 1),
		4: ("minimal"			, _("List style: minimal")			, 45		, 1)
	},

	"template_attributes": {
		"start": 5,
		"spacer": 15,
		"bar_size": (90, 14),
		"icon_size": (45, 35),
		"picon_size": (55, 35),
		"date_width": 230,
		"length_width": 230,
		"progress_width": 150,
		"yoffs": 3,
		"font_sizes": [32, 30, 28],
		# optional: color, color_sel, recording_color, recording_color_sel, selection_color, selection_color_sel
	},

	"templates": {
		"default": (row_height[0], [
			# +-----------------------------------------------------+
			# | name				| date		|
			# +-----------------------------------------------------+
			# | description				| length	|
			# +-----------------------------------------------------+
			# | service name			| progress bar	|
			# +-----------------------------------------------------+
			# line 1 of 3: | name | date |
			MultiContentEntryText(
				pos=(start, (line_height[0] * 0 + (line_height[0] - font_height[0]) / 2) + yoffs),
				size=(width - start - date_width - spacer, font_height[0]),
				font=0, flags=RT_HALIGN_LEFT, text=1, color=0xFF000008, color_sel=0xFF000008), 					# name
			MultiContentEntryText(
				pos=(width - date_width, (line_height[0] * 0 + (line_height[0] - font_height[2]) / 2) + yoffs),
				size=(date_width, font_height[2]),
				font=2, flags=RT_HALIGN_RIGHT, text=5, color=0xFF000007, color_sel=0xFF000008), 				# date

			# line 2 of 3: | description | length |
			MultiContentEntryText(
				pos=(start, (line_height[0] * 1 + (line_height[0] - font_height[2]) / 2)),
				size=(width - start - length_width, font_height[2]),
				text=4, font=2, flags=RT_HALIGN_LEFT, color=0xFF000007, color_sel=0xFF000008), 					# description
			MultiContentEntryText(
				pos=(width - length_width, (line_height[0] * 1 + (line_height[0] - font_height[2]) / 2)),
				size=(length_width, font_height[2]),
				text=6, font=2, flags=RT_HALIGN_RIGHT, color=0xFF000007, color_sel=0xFF000008), 				# length

			# line 3 of 3: | service name | progress bar|
			MultiContentEntryText(
				pos=(start, (line_height[0] * 2 + (line_height[0] - font_height[2]) / 2) - yoffs),
				size=(width - start - bar_size[0] - spacer, font_height[2]),
				text=3, font=2, flags=RT_HALIGN_LEFT, color=0xFF000007, color_sel=0xFF000008), 					# service name
			MultiContentEntryProgressPixmap(
				pos=(width - bar_size[0], (line_height[0] * 2 + (line_height[0] - bar_size[1]) / 2) - yoffs),
				size=bar_size, png=11, percent=-9, foreColor=0xFF000007, borderWidth=1), 					# progress bar
		]),
		"compact_description": (row_height[1], [
			# +-----------------------------------------------------+
			# | name				| date		|
			# +-----------------------------------------------------+
			# | description				| progress %	|
			# +-----------------------------------------------------+
			# line 1 of 2: | name  | date |
			MultiContentEntryText(
				pos=(start, (line_height[1] * 0 + (line_height[1] - font_height[1]) / 2) + yoffs),
				size=(width - start - date_width - spacer, font_height[1]),
				text=1, font=1, flags=RT_HALIGN_LEFT, color=0xFF000008, color_sel=0xFF000008), 					# name
			MultiContentEntryText(
				pos=(width - date_width, (line_height[1] * 0 + (line_height[1] - font_height[2]) / 2) + yoffs),
				size=(date_width, font_height[2]),
				text=5, font=2, flags=RT_HALIGN_RIGHT, color=0xFF000007, color_sel=0xFF000008), 				# date

			# line 2 of 2: | description | progress |
			MultiContentEntryText(
				pos=(start, (line_height[1] * 1 + (line_height[1] - font_height[2]) / 2) - yoffs),
				size=(width - start - progress_width - spacer, font_height[2]),
				text=4, font=2, flags=RT_HALIGN_LEFT, color=0xFF000007, color_sel=0xFF000008), 					# description
			MultiContentEntryText(
				pos=(width - progress_width, (line_height[1] * 1 + (line_height[1] - font_height[2]) / 2) - yoffs),
				size=(progress_width, font_height[2]),
				text=10, font=2, flags=RT_HALIGN_RIGHT, color=0xFF000007, color_sel=0xFF000008), 				# progress %
		]),
		"compact": (row_height[2], [
			# +-----------------------------------------------------+
			# | name				| date		|
			# +-----------------------------------------------------+
			# | description				| progress bar	|
			# +-----------------------------------------------------+
			# line 1 of 2: | name  | date |
			MultiContentEntryText(
				pos=(start, (line_height[2] * 0 + (line_height[2] - font_height[1]) / 2) + yoffs),
				size=(width - start - date_width - spacer, font_height[1]),
				text=1, font=1, flags=RT_HALIGN_LEFT, color=0xFF000008, color_sel=0xFF000008), 					# name
			MultiContentEntryText(
				pos=(width - date_width, (line_height[2] * 0 + (line_height[2] - font_height[2]) / 2) + yoffs),
				size=(date_width, font_height[2]),
				text=5, font=2, flags=RT_HALIGN_RIGHT, color=0xFF000007, color_sel=0xFF000008), 				# date

			# line 2 of 2: | description | progress |
			MultiContentEntryText(
				pos=(start, (line_height[2] * 1 + (line_height[2] - font_height[2]) / 2) - yoffs),
				size=(width - start - progress_width - spacer, font_height[2]),
				text=4, font=2, flags=RT_HALIGN_LEFT, color=0xFF000007, color_sel=0xFF000008), 					# description
			MultiContentEntryProgressPixmap(
				pos=(width - bar_size[0], (line_height[2] * 1 + (line_height[2] - bar_size[1]) / 2) - yoffs),
				size=bar_size, percent=-9, png=11, foreColor=0xFF000007, borderWidth=1), 					# progress bar
		]),
		"compact_single": (row_height[3], [
			# +-----------------------------------------------------+
			# | icon | picon | name		| progress bar | date	|
			# +-----------------------------------------------------+
			# line 1 of 1: | icon | picon | name | progress bar | date |
			MultiContentEntryPixmapAlphaBlend(
				pos=(start, (line_height[3] * 0 + (line_height[3] - icon_size[1]) / 2)),
				size=icon_size, png=12), 											# icon
			MultiContentEntryPixmapAlphaBlend(
				pos=(start + icon_size[0] + spacer, (line_height[3] * 0 + (line_height[3] - picon_size[1]) / 2)),
				size=picon_size, png=13), 											# picon
			MultiContentEntryText(
				pos=(start + icon_size[0] + spacer + picon_size[0] + spacer, (line_height[3] * 0 + (line_height[3] - font_height[2]) / 2)),
				size=(width - start - icon_size[0] - picon_size[0] - date_width - bar_size[0] - 4 * spacer, font_height[2]),
				text=1, font=2, flags=RT_HALIGN_LEFT, color=0xFF000007, color_sel=0xFF000008), 					# name
			MultiContentEntryProgressPixmap(
				pos=(width - date_width - bar_size[0] - spacer, (line_height[3] * 0 + (line_height[3] - bar_size[1]) / 2)),
				size=bar_size, percent=- 9, png=11, foreColor=0xFF000007, borderWidth=1), 					# progress bar
			MultiContentEntryText(
				pos=(width - date_width, (line_height[3] * 0 + (line_height[3] - font_height[2]) / 2)),
				size=(date_width, font_height[2]),
				text=5, font=2, flags=RT_HALIGN_CENTER, color=0xFF000007, color_sel=0xFF000008), 				# date
		]),
		"minimal": (row_height[4], [
			# +-----------------------------------------------------+
			# | name			| progress bar | date 	|
			# +-----------------------------------------------------+
			# line 1 of 1: | name | progress bar | date |
			MultiContentEntryText(
				pos=(start, (line_height[4] * 0 + (line_height[4] - font_height[0]) / 2)),
				size=(width - start - date_width - spacer - bar_size[0] - spacer, font_height[0]),
				text=1, font=0, flags=RT_HALIGN_LEFT, color=0xFF000007, color_sel=0xFF000008), 					# name
			MultiContentEntryProgressPixmap(
				pos=(width - date_width - bar_size[0] - spacer, (line_height[4] * 0 + (line_height[4] - bar_size[1]) / 2)),
				size=bar_size, percent=-9, png=11, foreColor=0xFF000007, borderWidth=1), 					# progress bar
			MultiContentEntryText(
				pos=(width - date_width, (line_height[4] * 0 + (line_height[4] - font_height[1]) / 2)), size=(date_width, font_height[1]),
				text=5, font=1, flags=RT_HALIGN_CENTER, color=0xFF000007, color_sel=0xFF000008), 				# date
		]),
	},

	"fonts": [gFont("Regular", font_sizes[0]), gFont("Regular", font_sizes[1]), gFont("Regular", font_sizes[2])]
}
