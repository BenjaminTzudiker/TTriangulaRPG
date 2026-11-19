/* pin.c (2026-11-17): one round of N attackers on one target, packet 0.11.0, with the designer's hold rule. Exact.

   Everyone is the level-1 sample fighter (HP 10, stamina 16, recovery 4, Melee Defense 3, armor 2, longsword 1d8+3 a
   step, base 2, critical on 7-8, Finesse 1, 6 free squares, 2 squares a dash). Open ground, on a line: the attackers
   start together, the target D squares away.

   Packet 0.11.0: one escalation (each action costs its base + the actions taken since your last turn ended), a dash is
   an action (1 + escalation, 2 squares), a dash phase before every turn (the first included); of those who want to
   dash the highest in initiative goes, then anyone may again. In the phase before attacker i's turn only attacker i and
   the target dash.

   The hold rule (designer, 2026-11-17):
     - at the end of its turn, after it recovers, an attacker next to the target may set any of its stamina aside as
       tokens on the target (HOLD=1). They take effect at once and are out until the holder's next turn.
     - leaving the holder costs 1 + tokens (first square; the hold then ends). If the target doesn't pay, the holder may
       make an opportunity attack, and the hold ends.
     - an opportunity attack is not an action: its steps cost 2, 3, 4, 5. It may cost at most CAP (1 + odd Finesse = 2)
       plus the tokens; tokens are spent first.
   With no tokens the same rules give the ordinary case: pay 1, or take an attack of at most CAP.

   Order of turns: the target's turn comes after TPOS attackers (TPOS=N: after all of them, which is outside the round
   and not played). On its turn (TPOS<N) the target may attack an adjacent attacker (the holder), then move: free
   movement and dashes, paying or not paying for each adjacent attacker as above. Then it recovers and its escalation
   resets.

   Payoff = P(target is down when the round ends) - LAM/100 * P(the target downs an attacker). Attackers maximise it,
   the target minimises it.

   Keys: N D K (most dashes by the target between resets) MD ARM HOLD CAP TPOS LAM COMPAT (1: twotarget.c's simpler
   leaving rule, for the self-check) QUIET TRACE. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
static int N=3, D=7, K=4, MD=3, ARM=2, HP0=10, ST0=16, AST=16, FREE=6, BASE=2, HOLD=1, CAP=2, TPOS=-1, LAM=0, COMPAT=0, QUIET=0, TRACE=0, REC=4, TMAXHP=10, HREC=1, HMAX=99, PRICE1=1, PAYALL=0;
typedef struct { int t, c; double p; } Out;
typedef struct { double p, q; } V;
static double LAMF=0;
static inline double sc(V v){ return v.p-LAMF*v.q; }
static inline V mk(double p,double q){ V v={p,q}; return v; }
#define BIG mk(2.0,0.0)
#define SMALL mk(-2.0,0.0)
static Out OUTS[5][128]; static int NOUT[5];
static int FN[48][5]; static int FC[48][5][20], FW[48][5][20];
static double DEAD[5][11][17];
static inline int imin(int a,int b){return a<b?a:b;} static inline int imax(int a,int b){return a>b?a:b;}
static inline int tri(int n){ return n*(n+1)/2; }
static const int OACOST[5]={0,2,5,9,14};   /* n steps of an opportunity attack with a base-2 weapon */
/* pre = ready stamina when the turn ends, before recovery. HREC=1: holds are set after recovering; HREC=0: before. */
static inline int tok_max(int pre){ int m = HREC ? imin(16,pre+REC) : pre; return imin(m,HMAX); }
static inline int r_after(int pre,int T){ return HREC ? imin(16,pre+REC)-T : imin(16-T, pre-T+REC); }

static void build(void){
  for(int s=1;s<=4;s++){ static double acc[48][5]; memset(acc,0,sizeof(acc)); int tot=1; for(int q=0;q<s;q++) tot*=8;
    for(int code=0;code<tot;code++){ int x=code,t=0,c=0; for(int q=0;q<s;q++){ int d=x%8+1; x/=8; t+=d+3; if(d>=7) c++; } acc[t][c]+=1.0/tot; }
    NOUT[s]=0; for(int t=0;t<48;t++) for(int c=0;c<5;c++) if(acc[t][c]>0){ OUTS[s][NOUT[s]].t=t; OUTS[s][NOUT[s]].c=c; OUTS[s][NOUT[s]].p=acc[t][c]; NOUT[s]++; } }
  for(int t=0;t<48;t++) for(int c=0;c<5;c++){ int best[17]; for(int q=0;q<17;q++) best[q]=999;
    for(int p=0;p<8;p++){ int cp=tri(p); if(cp>16) break;
      for(int g=0;g<=16-cp;g++){ int left=imax(0,t-MD*(p+g)); int rem=imax(0,t-MD*p); int leak=imin(g,(rem+MD-1)/MD);
        int w=imax(0,left+leak-imax(0,ARM-c)); if(w>0) w+=c; if(w<best[cp+g]) best[cp+g]=w; if(left==0) break; } }
    FN[t][c]=0; int cur=999; for(int q=0;q<17;q++) if(best[q]<cur){ cur=best[q]; FC[t][c][FN[t][c]]=q; FW[t][c][FN[t][c]]=cur; FN[t][c]++; } }
  for(int s=1;s<=4;s++) for(int hp=1;hp<=10;hp++) for(int st=0;st<=16;st++){ double dead=0;
    for(int o=0;o<NOUT[s];o++){ int t=OUTS[s][o].t,c=OUTS[s][o].c, ok=0; for(int q=0;q<FN[t][c];q++) if(FC[t][c][q]<=st && FW[t][c][q]<hp){ ok=1; break; } if(!ok) dead+=OUTS[s][o].p; }
    DEAD[s][hp][st]=dead; }
}

/* ---- state ---- */
typedef struct { int hp, st, esc, pos; } Tg;                 /* the target: HP, ready stamina, escalation, distance from the attackers' start */
typedef struct { int n, T[2], r[2]; } Hs;                    /* attackers that have acted and stand next to the target: tokens, ready stamina */
static inline uint64_t pk_t(Tg t){ return (uint64_t)t.hp | ((uint64_t)t.st<<4) | ((uint64_t)t.esc<<9) | ((uint64_t)t.pos<<12); }             /* 18 bits */
static inline uint64_t pk_h(Hs h){ uint64_t k=h.n; for(int a=0;a<2;a++){ int T=a<h.n?h.T[a]:0, r=a<h.n?h.r[a]:0; k|=((uint64_t)T<<(2+10*a)) | ((uint64_t)r<<(7+10*a)); } return k; }   /* 22 bits */
#ifndef HBITS
#define HBITS 25
#endif
static uint64_t *HK; static V *HV; static long HUSED=0;
static inline uint64_t mkkey(int type,int i,Tg t,int x,Hs h,int tdone,int stage,int extra){
  return 1ULL | ((uint64_t)type<<1) | ((uint64_t)i<<4) | ((uint64_t)x<<6) | ((uint64_t)tdone<<9) | ((uint64_t)stage<<10) | ((uint64_t)extra<<12) | (pk_t(t)<<16) | (pk_h(h)<<34); }
static inline long hslot(uint64_t k){ uint64_t h=k*0x9E3779B97F4A7C15ULL; long i=(long)(h>>(64-HBITS)); while(HK[i] && HK[i]!=k) i=(i+1)&((1L<<HBITS)-1); return i; }
static inline int memo_get(uint64_t k,V *v){ long s=hslot(k); if(HK[s]){ *v=HV[s]; return 1; } return 0; }
static inline void memo_put(uint64_t k,V v){ long s=hslot(k); HK[s]=k; HV[s]=v; HUSED++; if(HUSED>(1L<<HBITS)*0.9){ fprintf(stderr,"hash table full\n"); exit(2);} }

static V W(int i,Tg t,int x,Hs h,int tdone);
static V E(int i,Tg t,int x,Hs h,int tdone);
static V TT(Tg t,Hs h);
static V LEAVE(int mode,int i,Tg t,int x,Hs h,int tdone,int stage);
static V AFTERTURN(Tg t,Hs h);
static inline int rcanon(int r,int tdone){ return (tdone || TPOS>=N) ? imin(r,CAP) : r; }   /* once the target can no longer attack it, only min(r,CAP) matters */

/* the target, after a blow of n steps: it picks the blocks. cont(...) is called with the new target state. */
typedef V (*Cont)(void *ctx, Tg t);
static V blow(int n, Tg t, Cont cont, void *ctx){
  V acc={0,0};
  for(int o=0;o<NOUT[n];o++){ int tt=OUTS[n][o].t, c=OUTS[n][o].c; V best=mk(1.0,0.0); /* down = 1 */
    for(int q=0;q<FN[tt][c];q++){ int bc=FC[tt][c][q], w=FW[tt][c][q]; if(bc>t.st) break; if(w>=t.hp) continue;
      Tg u=t; u.hp=t.hp-w; u.st=imin(t.st-bc, 6+u.hp); V v=cont(ctx,u); if(sc(v)<sc(best)) best=v; }
    acc.p+=OUTS[n][o].p*best.p; acc.q+=OUTS[n][o].p*best.q; }
  return acc;
}

/* ---- leaving: the target has paid for its movement; now each adjacent attacker in turn ---- */
typedef struct { int mode,i,x,tdone,stage; Hs h; } LCtx;
static V leave_cont(void *vc, Tg t){ LCtx *c=(LCtx*)vc; return LEAVE(c->mode,c->i,t,c->x,c->h,c->tdone,c->stage+1); }
static V AFTERTURN(Tg t,Hs h);
static V LEAVE(int mode,int i,Tg t,int x,Hs h,int tdone,int stage){
  if(stage>=h.n){ Hs none={0,{0,0},{0,0}}; return mode==0 ? W(i,t,x,none,tdone) : AFTERTURN(t,none); }
  uint64_t k=mkkey(2,i,t,x,h,tdone,stage,mode); V v; if(memo_get(k,&v)) return v;
  int T=h.T[stage], r=h.r[stage];
  V best=BIG;
  if(COMPAT){ /* twotarget.c: one stamina in all for leaving, no attack */
    int price=(stage==0)?1:0; if(t.st>=price){ Tg u=t; u.st-=price; best=LEAVE(mode,i,u,x,h,tdone,stage+1); }
    memo_put(k,best); return best; }
  int price=1+T;
  if(PAYALL && mode!=3 && T>0 && t.st<price && t.st>=1) price=t.st;   /* can't pay 1 + tokens: pay all you have (at least 1); not when later dashes are still to be paid */
  if(t.st>=price){ Tg u=t; u.st-=price; best=LEAVE(mode,i,u,x,h,tdone,stage+1); }
  /* or don't pay: the holder may attack with up to CAP + T, tokens first */
  { int budget=T+imin(CAP,r); V worst=LEAVE(mode,i,t,x,h,tdone,stage+1); /* the holder declines */
    LCtx c={mode,i,x,tdone,stage,h};
    for(int n=1;n<=4 && OACOST[n]<=budget;n++){ V vv=blow(n,t,leave_cont,&c); if(sc(vv)>sc(worst)) worst=vv; }
    if(sc(worst)<sc(best)) best=worst; }
  memo_put(k,best); return best;
}

/* ---- the dash phase before attacker i's turn ---- */
static V W(int i,Tg t,int x,Hs h,int tdone){
  if(i==TPOS && !tdone) return TT(t,h);
  if(i>=N) return mk(0,0);
  uint64_t k=mkkey(0,i,t,x,h,tdone,0,0); V v; if(memo_get(k,&v)) return v;
  int d=imax(1,t.pos-2*x);
  V closeV=E(i,t,x,h,tdone);
  V tdash=BIG;      /* the target dashes away 2 squares */
  if(t.esc<K){ int cost=1+t.esc+((d<=1 && !COMPAT)?1:0); if(COMPAT && h.n==0 && d<=1) cost+=1;
    if(cost<=t.st){ Tg u=t; u.st-=cost; u.esc++; u.pos+=2; tdash=LEAVE(0,i,u,x,h,tdone,0); } }
  V adash=SMALL;     /* attacker i dashes 2 squares closer */
  if(d>1 && tri(x+1)<=AST) adash=W(i,t,x+1,h,tdone);
  V best;
  if(i<TPOS){ V stay=closeV; if(sc(tdash)<sc(stay)) stay=tdash; best=stay; if(sc(adash)>sc(best)) best=adash; }      /* the attacker is higher in initiative */
  else      { V stay=closeV; if(sc(adash)>sc(stay)) stay=adash; best=stay; if(sc(tdash)<sc(best)) best=tdash; }      /* the target is higher */
  memo_put(k,best); return best;
}

/* ---- attacker i's turn ---- */
typedef struct { int i,x,tdone,ready; Hs h; } ECtx;
static V hold_choice(int i,Tg t,Hs h,int tdone,int pre){
  if(i+1>=N) return mk(0,0);                       /* the round is over */
  V best=SMALL; int lo=0, hi=tok_max(pre);
  if(!HOLD){ Hs g=h; if(g.n<2){ g.T[g.n]=0; g.r[g.n]=rcanon(r_after(pre,0),tdone); g.n++; } return W(i+1,t,0,g,tdone); }
  if((tdone || TPOS>=N) && HMAX>=99) lo=imax(0,hi-CAP-REC);   /* nobody can attack this holder: only the last few points of ready stamina matter */
  for(int T=lo;T<=hi;T++){ Hs g=h; if(g.n<2){ g.T[g.n]=T; g.r[g.n]=rcanon(r_after(pre,T),tdone); g.n++; } V v=W(i+1,t,0,g,tdone); if(sc(v)>sc(best)) best=v; }
  return best;
}
static V e_cont(void *vc, Tg t){ ECtx *c=(ECtx*)vc; return hold_choice(c->i,t,c->h,c->tdone,c->ready); }   /* ready here = pre */
static V E(int i,Tg t,int x,Hs h,int tdone){
  uint64_t k=mkkey(1,i,t,x,h,tdone,0,0); V v; if(memo_get(k,&v)) return v;
  int d=imax(1,t.pos-2*x), need=imax(0,d-1-FREE), m=(need+1)/2, cost=tri(x), cnt=x;
  for(int q=0;q<m;q++){ cost+=1+cnt; cnt++; }
  V best=(i+1>=N)?mk(0,0):W(i+1,t,0,h,tdone);          /* it stays where it is */
  if(cost<=AST){
    int kmax=0, c2=cost; while(kmax<4 && c2+BASE+cnt+kmax<=AST){ c2+=BASE+cnt+kmax; kmax++; }
    for(int ks=(COMPAT?imax(kmax,1):0); ks<=kmax; ks++){ int tot=cost; for(int j=0;j<ks;j++) tot+=BASE+cnt+j;
      int ready=AST-tot; V vv;   /* before recovery */
      if(ks==0) vv=hold_choice(i,t,h,tdone,ready);
      else if(i+1>=N) vv=mk(DEAD[ks][t.hp][t.st],0);
      else { ECtx c={i,x,tdone,ready,h}; vv=blow(ks,t,e_cont,&c); }
      if(sc(vv)>sc(best)) best=vv; } }
  memo_put(k,best); return best;
}

/* ---- the target's own turn (TPOS<N) ---- */
static V AFTERTURN(Tg t,Hs h){ t.esc=0; t.st=imin(t.st+REC,6+t.hp); for(int a=0;a<h.n;a++) h.r[a]=imin(h.r[a],CAP); return W(TPOS,t,0,h,1); }
static V move_choice(Tg t,int esc,Hs h,int *bj){   /* stay, or leave: free movement plus j dashes */
  t.esc=0;
  V best=AFTERTURN(t,h); if(bj) *bj=-1;
  int cost=0;
  for(int j=0;j<=K;j++){ if(j>0){ cost+=1+esc; esc++; } if(cost>t.st) break;
    Tg u=t; u.st-=cost; u.pos+=FREE+2*j; V v=LEAVE((PAYALL && j>=2)?3:1,0,u,0,h,0,0); if(sc(v)<sc(best)){ best=v; if(bj) *bj=j; } }
    /* (all j dashes are paid before leaving here; the first dash may come before the first square left, the rest can't be paid after paying everything) */
  return best;
}
/* the target attacks holder a with ks steps: the value, and optionally the most likely branch */
static V stab(Tg t,Hs h,int a,int ks,int cost){
  Tg u=t; u.st-=cost; int esc2=t.esc+ks; V acc={0,0};
  for(int o=0;o<NOUT[ks];o++){ int tt=OUTS[ks][o].t, c=OUTS[ks][o].c; int alive=0, spent=0;
    for(int q=0;q<FN[tt][c];q++){ if(FC[tt][c][q]>h.r[a]) break; if(FW[tt][c][q]<10){ alive=1; spent=FC[tt][c][q]; } }
    Hs g=h; double add=0;
    if(alive){ g.r[a]=h.r[a]-spent; }
    else { add=1.0; for(int b=a;b<g.n-1;b++){ g.T[b]=g.T[b+1]; g.r[b]=g.r[b+1]; } g.n--; }
    V v=move_choice(u,esc2,g,NULL); acc.p+=OUTS[ks][o].p*v.p; acc.q+=OUTS[ks][o].p*(v.q+add); }
  return acc;
}
static V TT(Tg t,Hs h){
  uint64_t k=mkkey(3,0,t,0,h,0,0,0); V v; if(memo_get(k,&v)) return v;
  V best=move_choice(t,t.esc,h,NULL);                                      /* no attack */
  for(int a=0;a<h.n;a++){ int cost=0;
    for(int ks=1;ks<=4;ks++){ cost+=BASE+t.esc+ks-1; if(cost>t.st) break;
      V acc=stab(t,h,a,ks,cost); if(sc(acc)<sc(best)) best=acc; } }
  memo_put(k,best); return best;
}

/* ---- a typical line of play: follow the best choices; at each blow take the most likely result ---- */
static void say_leave(Tg *t,Hs *h){   /* the target has moved off: pay or not, holder by holder (most likely results) */
  for(int a=0;a<h->n;a++){ int T=h->T[a], r=h->r[a], price=1+T, budget=T+imin(CAP,r);
    int nmax=0; for(int n=1;n<=4 && OACOST[n]<=budget;n++) nmax=n;
    if(t->st>=price && (nmax==0 || price<=3*nmax)){ t->st-=price; printf("pays %d to leave the holder; ",price); }
    else if(nmax==0) printf("leaves the holder, which can't afford an attack; ");
    else { int bo=0; for(int o=1;o<NOUT[nmax];o++) if(OUTS[nmax][o].p>OUTS[nmax][bo].p) bo=o;
      int tt=OUTS[nmax][bo].t, c=OUTS[nmax][bo].c, done=0;
      for(int q=FN[tt][c]-1;q>=0;q--){ int bc=FC[tt][c][q], w=FW[tt][c][q]; if(bc<=t->st && w<t->hp){ t->hp-=w; t->st=imin(t->st-bc,6+t->hp); done=1; break; } }
      if(!done){ printf("doesn't pay; the holder's %d-step attack (typical roll %d) downs it; ",nmax,tt); t->hp=0; return; }
      printf("doesn't pay; takes a %d-step attack (typical roll %d): %d HP, %d stamina; ",nmax,tt,t->hp,t->st); } }
  h->n=0;
}
static void trace(void){
  Tg t={HP0,ST0,0,D}; Hs h={0,{0,0},{0,0}}; int tdone=0;
  for(int i=0;i<N;i++){
    if(i==TPOS && !tdone){
      printf("   TARGET'S TURN (HP %d, stamina %d, escalation %d",t.hp,t.st,t.esc); if(h.n) printf("; holder has %d token(s) on it and %d ready",h.T[0],h.r[0]); printf("): ");
      int bj; V best=move_choice(t,t.esc,h,&bj); int ba=-1,bk=0,bc=0;
      for(int a=0;a<h.n;a++){ int cost=0; for(int ks=1;ks<=4;ks++){ cost+=BASE+t.esc+ks-1; if(cost>t.st) break; V acc=stab(t,h,a,ks,cost); if(sc(acc)<sc(best)-1e-12){ best=acc; ba=a; bk=ks; bc=cost; } } }
      int esc=t.esc;
      if(ba>=0){ /* most likely result of the stab */
        int bo=0; for(int o=1;o<NOUT[bk];o++) if(OUTS[bk][o].p>OUTS[bk][bo].p) bo=o;
        int tt=OUTS[bk][bo].t, c=OUTS[bk][bo].c, alive=0, spent=0; double pd=0;
        for(int o=0;o<NOUT[bk];o++){ int ok=0; for(int q=0;q<FN[OUTS[bk][o].t][OUTS[bk][o].c];q++){ if(FC[OUTS[bk][o].t][OUTS[bk][o].c][q]>h.r[ba]) break; if(FW[OUTS[bk][o].t][OUTS[bk][o].c][q]<10) ok=1; } if(!ok) pd+=OUTS[bk][o].p; }
        for(int q=0;q<FN[tt][c];q++){ if(FC[tt][c][q]>h.r[ba]) break; if(FW[tt][c][q]<10){ alive=1; spent=FC[tt][c][q]; } }
        printf("it attacks the holder with %d step(s) for %d stamina (the holder goes down %.0f%% of the time; typical roll %d: %s); ",bk,bc,100*pd,tt,alive?"it stays up":"it goes down");
        t.st-=bc; esc+=bk; if(alive) h.r[ba]-=spent; else h.n=0;
        move_choice(t,esc,h,&bj); }
      if(bj<0) printf("it stays where it is");
      else { int cost=0; for(int j=1;j<=bj;j++){ cost+=1+esc; esc++; } t.st-=cost; t.pos+=FREE+2*bj; printf("it moves %d squares away (%d dash(es), %d stamina); ",FREE+2*bj,bj,cost); say_leave(&t,&h); if(t.hp<=0){ printf("\n"); return; } }
      t.esc=0; t.st=imin(t.st+REC,6+t.hp); for(int a=0;a<h.n;a++) h.r[a]=imin(h.r[a],CAP); tdone=1;
      printf(" -> ends its turn with %d HP, %d stamina, gap from the start %d\n",t.hp,t.st,t.pos);
    }
    int x=0; printf("   before attacker %d: ",i+1);
    for(;;){ int d=imax(1,t.pos-2*x); V closeV=E(i,t,x,h,tdone), tdash=BIG, adash=SMALL; Tg u=t;
      if(t.esc<K){ int cost=1+t.esc+(d<=1?1:0); if(cost<=t.st){ u.st-=cost; u.esc++; u.pos+=2; tdash=LEAVE(0,i,u,x,h,tdone,0); } }
      if(d>1 && tri(x+1)<=AST) adash=W(i,t,x+1,h,tdone);
      V cur=W(i,t,x,h,tdone);
      if(i<TPOS){ if(sc(adash)>-1.5 && fabs(sc(adash)-sc(cur))<1e-12 && sc(adash)>fmin(sc(closeV),sc(tdash))+1e-12){ printf("attacker dashes; "); x++; continue; }
                  if(sc(tdash)<1.5 && sc(tdash)<sc(closeV)-1e-12){ printf("target dashes away (%d stamina left); ",u.st); t=u; say_leave(&t,&h); if(t.hp<=0){ printf("\n"); return; } continue; } }
      else      { if(sc(tdash)<1.5 && fabs(sc(tdash)-sc(cur))<1e-12 && sc(tdash)<fmax(sc(closeV),sc(adash))-1e-12){ printf("target dashes away (%d stamina left); ",u.st); t=u; say_leave(&t,&h); if(t.hp<=0){ printf("\n"); return; } continue; }
                  if(sc(adash)>-1.5 && sc(adash)>sc(closeV)+1e-12){ printf("attacker dashes; "); x++; continue; } }
      break; }
    int d=imax(1,t.pos-2*x), need=imax(0,d-1-FREE), m=(need+1)/2, cost=tri(x), cnt=x; for(int q=0;q<m;q++){ cost+=1+cnt; cnt++; }
    printf("gap %d, attacker has dashed %d", d, x);
    if(cost>AST){ printf("; it can't reach\n"); continue; }
    int kmax=0, c2=cost; while(kmax<4 && c2+BASE+cnt+kmax<=AST){ c2+=BASE+cnt+kmax; kmax++; }
    int bk=-1; V bv=(i+1>=N)?mk(0,0):W(i+1,t,0,h,tdone);
    for(int ks=0;ks<=kmax;ks++){ int tot=cost; for(int j=0;j<ks;j++) tot+=BASE+cnt+j; int ready=AST-tot; V vv;
      if(ks==0) vv=hold_choice(i,t,h,tdone,ready); else if(i+1>=N) vv=mk(DEAD[ks][t.hp][t.st],0); else { ECtx c={i,x,tdone,ready,h}; vv=blow(ks,t,e_cont,&c); }
      if(sc(vv)>sc(bv)+1e-12){ bv=vv; bk=ks; } }
    if(bk<0){ printf("; it does nothing that changes the result\n"); continue; }
    int tot=cost; for(int j=0;j<bk;j++) tot+=BASE+cnt+j; int ready=AST-tot;
    printf("; on its turn it dashes %d more and makes %d step(s) (%d stamina spent in all)", m, bk, tot);
    if(bk>0){ /* most likely result, target's best blocks */
      int bo=0; for(int o=1;o<NOUT[bk];o++) if(OUTS[bk][o].p>OUTS[bk][bo].p) bo=o;
      int tt=OUTS[bk][bo].t, c=OUTS[bk][bo].c; V best=mk(1,0); Tg bu=t; int ok=0;
      for(int q=0;q<FN[tt][c];q++){ int bc=FC[tt][c][q], w=FW[tt][c][q]; if(bc>t.st) break; if(w>=t.hp) continue;
        Tg u=t; u.hp=t.hp-w; u.st=imin(t.st-bc,6+u.hp); V v=(i+1>=N)?mk(0,0):hold_choice(i,u,h,tdone,ready); if(!ok || sc(v)<sc(best)){ best=v; bu=u; ok=1; } }
      if(!ok){ printf("; a typical roll of %d downs the target (it goes down %.0f%% of the time here)\n",tt,100*DEAD[bk][t.hp][t.st]); return; }
      printf("; typical roll %d: target blocks to %d HP, %d stamina", tt, bu.hp, bu.st); t=bu; }
    if(i+1<N && HOLD){ int bT=0; V b2=SMALL; for(int T=0;T<=tok_max(ready);T++){ Hs g=h; g.T[g.n]=T; g.r[g.n]=rcanon(r_after(ready,T),tdone); g.n++; V v=W(i+1,t,0,g,tdone); if(sc(v)>sc(b2)+1e-12){ b2=v; bT=T; } }
      printf("; it ends with %d ready before recovering and sets %d token(s), keeping %d", ready, bT, r_after(ready,bT)); h.T[h.n]=bT; h.r[h.n]=rcanon(r_after(ready,bT),tdone); h.n++; }
    else if(i+1<N){ h.T[h.n]=0; h.r[h.n]=rcanon(r_after(ready,0),tdone); h.n++; }
    printf("\n");
  }
}
int main(int argc,char **argv){
  for(int a=1;a<argc;a++){ char *eq=strchr(argv[a],'='); if(!eq) continue; *eq=0; int v=atoi(eq+1); const char *k=argv[a];
    #define P(n,var) if(!strcmp(k,n)) var=v;
    P("N",N) P("D",D) P("K",K) P("MD",MD) P("ARM",ARM) P("HOLD",HOLD) P("CAP",CAP) P("TPOS",TPOS) P("LAM",LAM) P("COMPAT",COMPAT) P("QUIET",QUIET) P("TRACE",TRACE) P("ST0",ST0) P("HP0",HP0) P("REC",REC) P("HREC",HREC) P("HMAX",HMAX) P("PAYALL",PAYALL) }
  if(TPOS<0) TPOS=N;
  LAMF=LAM/100.0;
  build(); HK=calloc(1L<<HBITS,sizeof(uint64_t)); HV=malloc((1L<<HBITS)*sizeof(V));
  Tg t={HP0,ST0,0,D}; Hs h={0,{0,0},{0,0}};
  V v=W(0,t,0,h,0);
  if(QUIET){ printf("%.10f %.10f\n",v.p,v.q); return 0; }
  printf("N=%d D=%d K=%d MD=%d HOLD=%d CAP=%d TPOS=%d LAM=%d HREC=%d HMAX=%d | target down %6.2f%% | an attacker downed by the target %6.2f%% | states %ld\n",N,D,K,MD,HOLD,CAP,TPOS,LAM,HREC,HMAX,100*v.p,100*v.q,HUSED);
  if(TRACE) trace();
  return 0;
}
