# Copyright (C) 2018-2025 by dream-alpha
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
				pos=(start, 0),
				size=(width - start - date_width - spacer, line_height[0]),
				font=1, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=1, color=0xFF000008, color_sel=0xFF000008), 		# name
			MultiContentEntryText(
				pos=(width - date_width, 0),
				size=(date_width, line_height[0]),
				font=2, flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER, text=5, color=0xFF000007, color_sel=0xFF000008), 		# date

			# line 2 of 3: | description | length |
			MultiContentEntryText(
				pos=(start, line_height[0]),
				size=(width - start - length_width, line_height[0]),
				text=4, font=2, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, color=0xFF000007, color_sel=0xFF000008), 		# description
			MultiContentEntryText(
				pos=(width - length_width, line_height[0]),
				size=(length_width, line_height[0]),
				text=6, font=2, flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER, color=0xFF000007, color_sel=0xFF000008), 		# length

			# line 3 of 3: | service name | progress bar|
			MultiContentEntryText(
				pos=(start, line_height[0] * 2),
				size=(width - start - bar_size[0] - spacer, line_height[0]),
				text=3, font=2, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, color=0xFF000007, color_sel=0xFF000008), 		# service name
			MultiContentEntryProgressPixmap(
				pos=(width - bar_size[0], line_height[0] * 2 + (line_height[0] - bar_size[1]) / 2),
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
				pos=(start, 0),
				size=(width - start - date_width - spacer, line_height[1]),
				text=1, font=1, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, color=0xFF000008, color_sel=0xFF000008), 		# name
			MultiContentEntryText(
				pos=(width - date_width, 0),
				size=(date_width, line_height[1]),
				text=5, font=2, flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER, color=0xFF000007, color_sel=0xFF000008), 		# date

			# line 2 of 2: | description | progress |
			MultiContentEntryText(
				pos=(start, line_height[1]),
				size=(width - start - progress_width - spacer, line_height[1]),
				text=4, font=2, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, color=0xFF000007, color_sel=0xFF000008), 		# description
			MultiContentEntryText(
				pos=(width - progress_width, line_height[1]),
				size=(progress_width, line_height[1]),
				text=10, font=2, flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER, color=0xFF000007, color_sel=0xFF000008), 		# progress %
		]),
		"compact": (row_height[2], [
			# +-----------------------------------------------------+
			# | name				| date		|
			# +-----------------------------------------------------+
			# | description				| progress bar	|
			# +-----------------------------------------------------+
			# line 1 of 2: | name  | date |
			MultiContentEntryText(
				pos=(start, 0),
				size=(width - start - date_width - spacer, line_height[2]),
				text=1, font=1, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, color=0xFF000008, color_sel=0xFF000008), 		# name
			MultiContentEntryText(
				pos=(width - date_width, 0),
				size=(date_width, line_height[2]),
				text=5, font=2, flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER, color=0xFF000007, color_sel=0xFF000008),		# date

			# line 2 of 2: | description | progress |
			MultiContentEntryText(
				pos=(start, line_height[2]),
				size=(width - start - progress_width - spacer, line_height[2]),
				text=4, font=2, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, color=0xFF000007, color_sel=0xFF000008), 		# description
			MultiContentEntryProgressPixmap(
				pos=(width - bar_size[0], line_height[2] + (line_height[2] - bar_size[1]) / 2),
				size=bar_size, percent=-9, png=11, foreColor=0xFF000007, borderWidth=1), 					# progress bar
		]),
		"compact_single": (row_height[3], [
			# +-----------------------------------------------------+
			# | icon | picon | name		| progress bar | date	|
			# +-----------------------------------------------------+
			# line 1 of 1: | icon | picon | name | progress bar | date |
			MultiContentEntryPixmapAlphaBlend(
				pos=(start, (line_height[3] - icon_size[1]) / 2),
				size=icon_size, png=12), 											# icon
			MultiContentEntryPixmapAlphaBlend(
				pos=(start + icon_size[0] + spacer, (line_height[3] - picon_size[1]) / 2),
				size=picon_size, png=13), 											# picon
			MultiContentEntryText(
				pos=(start + icon_size[0] + spacer + picon_size[0] + spacer, 0),
				size=(width - start - icon_size[0] - picon_size[0] - date_width - bar_size[0] - 4 * spacer, line_height[3]),
				text=1, font=2, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, color=0xFF000007, color_sel=0xFF000008), 		# name
			MultiContentEntryProgressPixmap(
				pos=(width - date_width - bar_size[0] - spacer, (line_height[3] - bar_size[1]) / 2),
				size=bar_size, percent=- 9, png=11, foreColor=0xFF000007, borderWidth=1), 					# progress bar
			MultiContentEntryText(
				pos=(width - date_width, 0),
				size=(date_width, line_height[3]),
				text=5, font=2, flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, color=0xFF000007, color_sel=0xFF000008), 		# date
		]),
		"minimal": (row_height[4], [
			# +-----------------------------------------------------+
			# | name			| progress bar | date 	|
			# +-----------------------------------------------------+
			# line 1 of 1: | name | progress bar | date |
			MultiContentEntryText(
				pos=(start, 0),
				size=(width - start - date_width - spacer - bar_size[0] - spacer, line_height[4]),
				text=1, font=1, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, color=0xFF000007, color_sel=0xFF000008), 		# name
			MultiContentEntryProgressPixmap(
				pos=(width - date_width - bar_size[0] - spacer, (line_height[4] - bar_size[1]) / 2),
				size=bar_size, percent=-9, png=11, foreColor=0xFF000007, borderWidth=1), 					# progress bar
			MultiContentEntryText(
				pos=(width - date_width, 0),
				size=(date_width, line_height[4]),
				text=5, font=2, flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, color=0xFF000007, color_sel=0xFF000008), 		# date
		]),
	},

	"fonts": [gFont("Regular", font_size[0]), gFont("Regular", font_size[1]), gFont("Regular", font_size[2])]
}
