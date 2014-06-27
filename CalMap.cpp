#include <cstdio>
#include <cstdlib>
#include <algorithm>
#include <vector>
#include <cstring>
#include <string>
#include <iostream>
using namespace std ;
double SingleMap ;
double MatchCnt ;
vector <string> Ret ;
vector <string> Ans ;
int RetSz , AnsSz ;
void ReadFiles( const char *f1 , const char *f2 )
{
    FILE *fin1 = fopen( f1 , "r" ) ;
    FILE *fin2 = fopen( f2 , "r" ) ;
    char W[300] ;
    Ret.clear() ;
    Ans.clear() ;
    // Intialize
    while( fgets( W , 300 , fin1 ) )
        Ret.push_back( W ) ;
    while( fgets( W , 300 , fin2 ) )
        Ans.push_back( W ) ;
    RetSz = Ret.size() ;
    AnsSz = Ans.size() ;
    fclose( fin1 ) ;
    fclose( fin2 ) ;
}
bool CheckMatch( int Target )
{
    bool Find = 0 ;
    for( int i = 0 ; i < AnsSz ; i++ )
        if( Ans[i] == Ret[Target] )
            Find = 1 ;
    return Find ;
}
int main( int argc , char *argv[ ] )
{
    double SinglePre ;
    // 1:Ret  2:Ans
    ReadFiles( argv[1] , argv[2] ) ;
    SingleMap = 0.0 ;
    MatchCnt  = 0.0 ;
    for( int i = 0 ; i < RetSz ; i++ )
        if( CheckMatch( i ) )
        {
            MatchCnt += 1.0 ;
            //printf( "%.2lf\n" , MatchCnt / (double)(i+1) ) ;
            SinglePre += MatchCnt / (double)(i+1) ;
        }
    SingleMap = SinglePre / (double)AnsSz ;
    //printf( "%.2lf / %.2lf , %d\n" , SingleMap , SinglePre , AnsSz ) ;
    printf( "%.2lf\n" , SingleMap ) ;
    return 0 ;
}
