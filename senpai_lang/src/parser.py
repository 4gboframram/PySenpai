import lark
parser = lark.Lark.open("grammar.lark", rel_to=__file__, keep_all_tokens=False)