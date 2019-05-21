# Generated from lsystem.g4 by ANTLR 4.6
from .lgrammar import antlr4
from .lgrammar.lsystemParser import lsystemParser
from .literal_semantic import (DrawTerminal, MoveTerminal, PopTerminal,
                               PushTerminal, RotateTerminal)
from .lsystem_class import Lsystem

# This class defines a complete generic visitor for a parse tree produced by
# lsystemParser. ctx.accept(self) visits the ctx


class lgrammarVisitor(antlr4.ParseTreeVisitor):
    # Visit a parse tree produced by lsystemParser#probability.

    def __init__(self):
        self.lsystem = Lsystem()

    def visitProbability(self, ctx: lsystemParser.ProbabilityContext):
        return ctx.FLOAT()

    # Visit a parse tree produced by lsystemParser#rand_entry.
    def visitRand_entry(self, ctx: lsystemParser.Rand_entryContext):
        floats = list(map(lambda x: float(x.getText()), ctx.FLOAT()))
        if len(floats) == 1:
            return floats[0]
        elif len(floats) == 2:
            if floats[0] > floats[1]:
                raise RuntimeError("Range is not in order. " + str(floats))
            elif floats[0] == floats[1]:
                return floats[0]
            return floats
        raise RuntimeError

    # Visit a parse tree produced by lsystemParser#rotation.
    def visitRotation(self, ctx: lsystemParser.RotationContext):
        rot_tuple = []
        for x in ctx.rand_entry():
            rot_tuple.append(x.accept(self))
        return RotateTerminal(*rot_tuple)

    # Visit a parse tree produced by lsystemParser#move.
    def visitMove(self, ctx: lsystemParser.MoveContext):
        if ctx.rand_entry() is None:
            return MoveTerminal()
        return MoveTerminal(ctx.rand_entry().accept(self))
    # Visit a parse tree produced by lsystemParser#draw.

    def visitDraw(self, ctx: lsystemParser.DrawContext):
        if ctx.rand_entry() is None:
            return DrawTerminal()
        return DrawTerminal(ctx.rand_entry().accept(self))

    # Visit a parse tree produced by lsystemParser#push.
    def visitPush(self, ctx: lsystemParser.PushContext):
        return PushTerminal()

    # Visit a parse tree produced by lsystemParser#pop.
    def visitPop(self, ctx: lsystemParser.PopContext):
        return PopTerminal()

    # Visit a parse tree produced by lsystemParser#term.
    def visitTerm(self, ctx: lsystemParser.TermContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by lsystemParser#non_term.
    def visitNon_term(self, ctx: lsystemParser.Non_termContext):
        return self.lsystem.get_non_terminal(ctx.NT().getText())

    # Visit a parse tree produced by lsystemParser#define_term.
    def visitDefine_term(self, ctx: lsystemParser.Define_termContext):
        return self.lsystem.get_define(ctx.DEFINE().getText())

    # Visit a parse tree produced by lsystemParser#init_sec.
    def visitInit_sec(self, ctx: lsystemParser.Init_secContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by lsystemParser#init_start.
    def visitInit_start(self, ctx: lsystemParser.Init_startContext):
        self.lsystem.start = ctx.non_term().accept(self)

    # Visit a parse tree produced by lsystemParser#define_sec.
    def visitDefine_sec(self, ctx: lsystemParser.Define_secContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by lsystemParser#define_entity.
    def visitDefine_entity(self, ctx: lsystemParser.Define_entityContext):
        define = self.lsystem.get_define(ctx.define_term().DEFINE().getText(), True)
        #define = ctx.define_term().accept(self)
        define.transition = ctx.define_res().accept(self)

    # Visit a parse tree produced by lsystemParser#define_res.
    def visitDefine_res(self, ctx: lsystemParser.Define_resContext):
        childs = ctx.getChildren(
            lambda x: isinstance(
                x, (lsystemParser.Non_termContext,
                    lsystemParser.TermContext)))
        return [x.accept(self) for x in childs]

    # Visit a parse tree produced by lsystemParser#rule_sec.
    def visitRule_sec(self, ctx: lsystemParser.Rule_secContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by lsystemParser#rule_entity.
    def visitRule_entity(self, ctx: lsystemParser.Rule_entityContext):
        nt = ctx.non_term().accept(self)
        if ctx.probability() is not None:
            nt.append_trans(ctx.rule_res().accept(self),
                            ctx.probability.accept(self))
        else:
            nt.append_trans(ctx.rule_res().accept(self))

    # Visit a parse tree produced by lsystemParser#rule_res.
    def visitRule_res(self, ctx: lsystemParser.Rule_resContext):
        childs = ctx.getChildren(
            lambda x: isinstance(
                x, (lsystemParser.Non_termContext,
                    lsystemParser.TermContext,
                    lsystemParser.Define_termContext)))
        return [x.accept(self) for x in childs]

    # Visit a parse tree produced by lsystemParser#final_sec.
    def visitFinal_sec(self, ctx: lsystemParser.Final_secContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by lsystemParser#final_rule_entity.
    def visitFinal_rule_entity(self,
                               ctx: lsystemParser.Final_rule_entityContext):
        nt = ctx.non_term().accept(self)
        nt.append_final_trans(ctx.final_rule_res().accept(self))

    # Visit a parse tree produced by lsystemParser#final_rule_res.
    def visitFinal_rule_res(self, ctx: lsystemParser.Final_rule_resContext):
        childs = ctx.getChildren(
            lambda x: isinstance(
                x, (lsystemParser.Non_termContext,
                    lsystemParser.TermContext,
                    lsystemParser.Define_termContext)))
        return [x.accept(self) for x in childs]

    # Visit a parse tree produced by lsystemParser#code.
    def visitCode(self, ctx: lsystemParser.CodeContext):
        self.visitChildren(ctx)
        return self.lsystem
