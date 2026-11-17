/* pursuit.c (2026-11-17): one pursuer P and one fleer F on a line, several rounds. Exact.

   Both are the level-1 sample fighter (stamina 6 + HP, recovery 4, Melee Defense 3, armor 2, longsword 1d8+3 a step,
   base 2, critical on 7-8, Finesse 1, 6 free squares, 2 squares a dash). P has 10 HP; F starts with HF HP. They
   start G squares apart (1 = adjacent). F wants to get away: it needs REM more squares to stand on an exit, and
   leaves the fight on its own turn once its movement that turn covers what is left. P wants to down F first.

   Rules: packet 0.11.0 (one escalation; a dash is an action, 1 + escalation, 2 squares; a dash phase before every
   turn, the higher in initiative first), with one of two opportunity-attack rules:
     HOLD=0  the packet's placeholder: paying off costs 1; an opportunity attack is one step for 2.
     HOLD=1  the designer's hold rule (2026-11-17): at the end of its turn, next to F, P may set stamina aside as
             tokens (after recovering if HREC=1, before if HREC=0; at most HMAX). They return when P's next turn
             starts. Leaving costs 1 + tokens, or P may attack with budget CAP + tokens (steps 2, 3, 4, 5; tokens
             first). Either way the hold ends.
   F may also turn and attack P on its own turn (FATK=1, up to 3 steps). F sets no holds.

   Order: PF=1, P acts first each round; PF=0, F first. The game lasts R rounds.
   Value = P(F is down). P maximises it, F minimises it. Reported with it: P(F got away), P(P down).
   Keys: HF G REM R PF HOLD HREC HMAX CAP K (F's most dashes between resets) KP (P's) FATK PST (P's stamina at
   the start) FST (F's; default its maximum) TRACE QUIET */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
static int HF=4, G=1, REM=16, R=5, PF=1, HOLD=1, HREC=1, HMAX=99, CAP=2, K=4, KP=5, FATK=1, PST=16, FST=-1, TRACE=0, QUIET=0, HSET=1, PAYALL=0, NEWHOLD=0;
static const int MD=3, ARM=2, REC=4, FREE=6, BASE=2;
typedef struct { int t, c; double p; } Out;
static Out OUTS[5][128]; static int NOUT[5];
static int FN[48][5]; static int FC[48][5][20], FW[48][5][20];
static inline int imin(int a,int b){return a<b?a:b;} static inline int imax(int a,int b){return a>b?a:b;}
static inline int tri(int n){ return n*(n+1)/2; }
static const int OACOST[5]={0,2,5,9,14};

static void build(void){
  for(int s=1;s<=4;s++){ static double acc[48][5]; memset(acc,0,sizeof(acc)); int tot=1; for(int q=0;q<s;q++) tot*=8;
    for(int code=0;code<tot;code++){ int x=code,t=0,c=0; for(int q=0;q<s;q++){ int d=x%8+1; x/=8; t+=d+3; if(d>=7) c++; } acc[t][c]+=1.0/tot; }
    NOUT[s]=0; for(int t=0;t<48;t++) for(int c=0;c<5;c++) if(acc[t][c]>0){ OUTS[s][NOUT[s]].t=t; OUTS[s][NOUT[s]].c=c; OUTS[s][NOUT[s]].p=acc[t][c]; NOUT[s]++; } }
  for(int t=0;t<48;t++) for(int c=0;c<5;c++){ int best[17]; for(int q=0;q<17;q++) best[q]=999;
    for(int p=0;p<8;p++){ int cp=tri(p); if(cp>16) break;
      for(int g=0;g<=16-cp;g++){ int left=imax(0,t-MD*(p+g)); int rem=imax(0,t-MD*p); int leak=imin(g,(rem+MD-1)/MD);
        int w=imax(0,left+leak-imax(0,ARM-c)); if(w>0) w+=c; if(w<best[cp+g]) best[cp+g]=w; if(left==0) break; } }
    FN[t][c]=0; int cur=999; for(int q=0;q<17;q++) if(best[q]<cur){ cur=best[q]; FC[t][c][FN[t][c]]=q; FW[t][c][FN[t][c]]=cur; FN[t][c]++; } }
}

/* value: three probabilities */
typedef struct { float d, e, k; } V;     /* F down, F escaped, P down */
static inline V mk(float d,float e,float k){ V v={d,e,k}; return v; }
/* P prefers a higher d, then a lower e; F the reverse. One scalar orders them. */
static inline double sc(V v){ return (double)v.d - 1e-4*(double)v.e - 1e-4*(double)v.k; }

typedef struct { int fhp,fst,fesc, php,pst,pesc, out,act, g,rem, r; } S;
#ifndef HBITS
#define HBITS 26
#endif
static uint64_t *HK; static V *HV; static long HUSED=0;
static inline uint64_t key(int type,S s,int extra){
  uint64_t k=1; int sh=1;
  #define PUT(v,b) k|=((uint64_t)(v))<<sh; sh+=b;
  PUT(type,3) PUT(s.fhp,4) PUT(s.fst,5) PUT(s.fesc,3) PUT(s.php,4) PUT(s.pst,5) PUT(s.pesc,3) PUT(s.out,5) PUT(s.act,1) PUT(s.g,6) PUT(s.rem,6) PUT(s.r,4) PUT(extra,4)
  return k; }
static inline long hslot(uint64_t k){ uint64_t h=k*0x9E3779B97F4A7C15ULL; long i=(long)(h>>(64-HBITS)); while(HK[i] && HK[i]!=k) i=(i+1)&((1L<<HBITS)-1); return i; }
static inline int memo_get(uint64_t k,V *v){ long s=hslot(k); if(HK[s]){ *v=HV[s]; return 1; } return 0; }
static inline void memo_put(uint64_t k,V v){ long s=hslot(k); HK[s]=k; HV[s]=v; HUSED++; if(HUSED>(1L<<HBITS)*0.85){ fprintf(stderr,"hash table full\n"); exit(2);} }

static V WPH(S s,int before);   /* the dash phase before P's turn (before=0) or F's turn (before=1) */
static V PT(S s);               /* P's turn */
static V FT(S s);               /* F's turn */
static V FM(S s);               /* F's turn after any attack: stay or move */
static const V FDOWN={1,0,0}, ESC={0,1,0}, PDOWN={0,0,1}, NONE={0,0,0};

static inline V after_p(S s){ if(!PF){ s.r++; if(s.r>R) return NONE; } return WPH(s,1); }   /* after P's turn comes F's dash phase */
static inline V after_f(S s){ if(PF){ s.r++; if(s.r>R) return NONE; } return WPH(s,0); }

/* P hits F with n steps; F picks its blocks (minimising). cont gets the new state. */
typedef V (*Cont)(void *ctx, S s);
static V hit_f(int n,S s,Cont cont,void *ctx){
  V acc={0,0,0};
  for(int o=0;o<NOUT[n];o++){ int tt=OUTS[n][o].t,c=OUTS[n][o].c; V best=FDOWN; double p=OUTS[n][o].p;
    for(int q=0;q<FN[tt][c];q++){ int bc=FC[tt][c][q], w=FW[tt][c][q]; if(bc>s.fst) break; if(w>=s.fhp) continue;
      S u=s; u.fhp-=w; u.fst=imin(s.fst-bc,6+u.fhp); V v=cont(ctx,u); if(sc(v)<sc(best)) best=v; }
    acc.d+=p*best.d; acc.e+=p*best.e; acc.k+=p*best.k; }
  return acc;
}
/* F hits P with n steps; P picks its blocks (maximising). */
static V hit_p(int n,S s,Cont cont,void *ctx){
  V acc={0,0,0};
  for(int o=0;o<NOUT[n];o++){ int tt=OUTS[n][o].t,c=OUTS[n][o].c; V best=PDOWN; int any=0; double p=OUTS[n][o].p;
    for(int q=0;q<FN[tt][c];q++){ int bc=FC[tt][c][q], w=FW[tt][c][q]; if(bc>s.pst) break; if(w>=s.php) continue;
      S u=s; u.php-=w; int top=6+u.php; u.pst=s.pst-bc;
      if(u.pst+u.out>top){ int over=u.pst+u.out-top; int cut=imin(over,u.pst); u.pst-=cut; over-=cut; u.out-=over; if(u.out==0) u.act=0; }
      V v=cont(ctx,u); if(!any || sc(v)>sc(best)){ best=v; any=1; } }
    acc.d+=p*best.d; acc.e+=p*best.e; acc.k+=p*best.k; }
  return acc;
}

/* F leaves P's reach: pay, or risk the attack. cont gets the state with the hold ended. */
static int NOPA=0;   /* set by FM: later dashes are still to be paid, so paying everything isn't possible */
static V leave(S s,Cont cont,void *ctx){
  int nopa=NOPA; NOPA=0;
  int T=(HOLD && s.act)?s.out:0, price=1+T;
  if(PAYALL && !nopa && T>0 && s.fst<price && s.fst>=1) price=s.fst;   /* the red team's fix: can't pay 1 + tokens? pay all you have (at least 1) */
  V best={2,0,0};
  if(s.fst>=price){ S u=s; u.fst-=price; u.act=0; best=cont(ctx,u); }
  /* don't pay */
  { S u=s; u.act=0; V worst=cont(ctx,u);        /* P declines */
    if(!HOLD){ if(s.pst>=BASE){ S w=s; w.pst-=BASE; V v=hit_f(1,w,cont,ctx); if(sc(v)>sc(worst)) worst=v; } }
    else { int budget=T+imin(CAP,s.pst);
      for(int n=1;n<=4 && OACOST[n]<=budget;n++){ int cost=OACOST[n], tok=imin(T,cost); S w=s; w.out-=tok; w.pst-=cost-tok; w.act=0;
        V v=hit_f(n,w,cont,ctx); if(sc(v)>sc(worst)) worst=v; } }
    if(sc(worst)<sc(best)) best=worst; }
  return best;
}

/* ---- dash phases ---- */
typedef struct { int before; } WCtx;
static V w_cont(void *vc,S s){ WCtx *c=(WCtx*)vc; int d=imin(2,s.rem); s.g+=d; s.rem-=d; return WPH(s,c->before); }
static V WPH(S s,int before){
  uint64_t k=key(before,s,0); V v; if(memo_get(k,&v)) return v;
  V endV = before==0 ? PT(s) : FT(s);
  V fV={2,0,0};
  if(s.rem>0 && s.fesc<K && 1+s.fesc<=s.fst){ S u=s; u.fst-=1+s.fesc; u.fesc++; WCtx c={before};
    if(s.g==1) fV=leave(u,w_cont,&c); else fV=w_cont(&c,u); }
  V pV={-2,0,0};
  if(s.g>1 && s.pesc<KP && 1+s.pesc<=s.pst){ S u=s; u.pst-=1+s.pesc; u.pesc++; u.g=imax(1,s.g-2); pV=WPH(u,before); }
  V best;
  if(PF){ V stay=endV; if(sc(fV)<sc(stay)) stay=fV; best=stay; if(sc(pV)>sc(best)) best=pV; }
  else  { V stay=endV; if(sc(pV)>sc(stay)) stay=pV; best=stay; if(sc(fV)<sc(best)) best=fV; }
  memo_put(k,best); return best;
}

/* ---- P's turn ---- */
static inline int tok_max(int pre,int top){ int m = HREC ? imin(top,pre+REC) : pre; return imin(m,HMAX); }
static inline int r_after(int pre,int T,int top){ return HREC ? imin(top,pre+REC)-T : imin(top-T, pre-T+REC); }
/* HSET=1: P only considers the token amounts that can matter: none, the thresholds where its attack can add a step
   (3, 7, 12 for budget 2 + T with steps 2, 3, 4, 5), F's ready stamina less 1 (paying leaves F empty) and F's ready
   stamina (F can't pay), and everything it can. This can only lower P's result: a lower bound. HSET=0 tries all. */
static int cand(int T,int fst,int mx){ if(T<0||T>mx) return 0; if(T==0||T==3||T==7||T==12||T==mx) return 1; if(T==fst||T==fst-1) return 1; return 0; }
static V p_end(S s,int adjacent){      /* s.pst = ready before recovering */
  int top=6+s.php, pre=s.pst+(NEWHOLD?s.out:0);   /* NEWHOLD: last turn's tokens come back now, right before recovery */
  s.pesc=0; s.out=0; s.act=0;
  if(!(HOLD && adjacent)){ s.pst=imin(top,pre+REC); return after_p(s); }
  V best={-2,0,0}; int mx=tok_max(pre,top);
  for(int T=0;T<=mx;T++){ if(HSET && !cand(T,s.fst,mx)) continue;
    S u=s; u.out=T; u.act=(T>0); u.pst=r_after(pre,T,top); V v=after_p(u); if(sc(v)>sc(best)) best=v; }
  return best;
}
static V pend_cont(void *vc,S s){ (void)vc; return p_end(s,1); }
static V p_adjacent(S u){              /* P stands next to F: any attack, then the end of its turn */
  V best=p_end(u,1); int c2=0;
  for(int ks=1;ks<=4;ks++){ c2+=BASE+u.pesc+ks-1; if(c2>u.pst) break; S w=u; w.pst-=c2;
    V vv=hit_f(ks,w,pend_cont,NULL); if(sc(vv)>sc(best)) best=vv; }
  return best;
}
static V PT(S s){
  uint64_t k=key(2,s,0); V v; if(memo_get(k,&v)) return v;
  if(!NEWHOLD){ s.pst+=s.out; s.out=0; s.act=0; }       /* tokens come back (NEWHOLD: they stay out through this turn) */
  V best;
  if(s.g==1) best=p_adjacent(s);
  else {
    best=p_end(s,0);                                     /* it stays where it is */
    int cost=0, esc=s.pesc;
    for(int j=0;;j++){
      if(j>0){ if(esc>=KP) break; cost+=1+esc; esc++; if(cost>s.pst) break; }
      int g2=imax(1,s.g-FREE-2*j);
      S u=s; u.pst-=cost; u.pesc=esc; u.g=g2;
      if(g2>1){ V vv=p_end(u,0); if(sc(vv)>sc(best)) best=vv; }
      else {
        if(s.g>2){ S w=u; w.g=2; V vv=p_end(w,0); if(sc(vv)>sc(best)) best=vv; }   /* stop one square short */
        V vv=p_adjacent(u); if(sc(vv)>sc(best)) best=vv;
        break; }
    }
  }
  memo_put(k,best); return best;
}

/* ---- F's turn ---- */
static V f_end(S s){ s.fesc=0; s.fst=imin(s.fst+REC,6+s.fhp); return after_f(s); }
typedef struct { int dist; } MCtx;
static V m_cont(void *vc,S s){ MCtx *c=(MCtx*)vc; if(c->dist>=s.rem) return ESC; s.g+=c->dist; s.rem-=c->dist; return f_end(s); }
static V FM(S s){
  uint64_t k=key(4,s,0); V v; if(memo_get(k,&v)) return v;
  V best=f_end(s);                                   /* it stays */
  if(s.rem==0) best=ESC;                             /* already on the exit: it leaves */
  int cost=0, esc=s.fesc;
  for(int j=0;j<=K;j++){ if(j>0){ if(esc>=K) break; cost+=1+esc; esc++; } if(cost>s.fst) break;
    S u=s; u.fst-=cost; u.fesc=esc; MCtx c={FREE+2*j}; V vv;
    if(s.g==1){ NOPA=(j>=2); vv=leave(u,m_cont,&c); } else vv=m_cont(&c,u);
    if(sc(vv)<sc(best)) best=vv;
    if(FREE+2*j>=s.rem) break; }
  memo_put(k,best); return best;
}
static V fm_cont(void *vc,S s){ (void)vc; return FM(s); }
static V FT(S s){
  uint64_t k=key(3,s,0); V v; if(memo_get(k,&v)) return v;
  V best=FM(s);
  if(FATK && s.g==1 && s.rem>0){ int cost=0;
    for(int ks=1;ks<=3;ks++){ cost+=BASE+s.fesc+ks-1; if(cost>s.fst) break; S u=s; u.fst-=cost; u.fesc=s.fesc+ks;
      V vv=hit_p(ks,u,fm_cont,NULL); if(sc(vv)<sc(best)) best=vv; } }
  memo_put(k,best); return best;
}

int main(int argc,char **argv){
  for(int a=1;a<argc;a++){ char *eq=strchr(argv[a],'='); if(!eq) continue; *eq=0; int v=atoi(eq+1); const char *k=argv[a];
    #define P(n,var) if(!strcmp(k,n)) var=v;
    P("HF",HF) P("G",G) P("REM",REM) P("R",R) P("PF",PF) P("HOLD",HOLD) P("HREC",HREC) P("HMAX",HMAX) P("CAP",CAP) P("K",K) P("KP",KP) P("FATK",FATK) P("PST",PST) P("FST",FST) P("TRACE",TRACE) P("QUIET",QUIET) P("HSET",HSET) P("PAYALL",PAYALL) P("NEWHOLD",NEWHOLD) }
  if(NEWHOLD) HREC=0;   /* holds come from stamina before recovering */
  build(); HK=calloc(1L<<HBITS,sizeof(uint64_t)); HV=malloc((1L<<HBITS)*sizeof(V));
  S s={HF, FST<0?6+HF:FST, 0, 10, PST, 0, 0,0, G, REM, 1};
  V v = PF ? WPH(s,0) : WPH(s,1);
  if(QUIET){ printf("%.6f %.6f %.6f\n",v.d,v.e,v.k); return 0; }
  printf("HF=%d G=%d REM=%d R=%d PF=%d HOLD=%d HREC=%d HMAX=%d HSET=%d PAYALL=%d NEWHOLD=%d FATK=%d | F down %6.2f%% | F away %6.2f%% | P down %6.2f%% | neither %6.2f%% | states %ld\n",
         HF,G,REM,R,PF,HOLD,HREC,HMAX,HSET,PAYALL,NEWHOLD,FATK,100*v.d,100*v.e,100*v.k,100*(1-v.d-v.e-v.k),HUSED);
  return 0;
}
