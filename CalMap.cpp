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
double Th ;
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
int EditDis( string A , string B )
{
    int Al = A.length() ;
    int Bl = B.length() ;
    int dp[ 50 ][ 50 ] ;
    memset( dp , 0 , sizeof( dp ) ) ;
    for( int i = 1 ; i <= Al ; i++ )
        dp[ i ][ 0 ] = dp[ i-1 ][ 0 ] + 1 ;
    for( int i = 1 ; i <= Bl ; i++ )
        dp[ 0 ][ i ] = dp[ 0 ][ i-1 ] + 1 ;
    for( int i = 1 ; i <= Al ; i++ )
        for( int j = 1 ; j <= Bl ; j++ )
        {
            int x1 = dp[i-1][j-1] + (A[i-1] == B[j-1] ? 0 : 2 ) ;
            int x2 = dp[i-1][j] + 1 ;
            int x3 = dp[i][j-1] + 1 ;
            dp[i][j] = min( min( x1 , x2 ) , x3 ) ;
        }
    return dp[Al][Bl] ;
}
bool CheckMatch( int Target )
{
    for( int i = 0 ; i < AnsSz ; i++ )
    {
        double Ec = (double) EditDis( Ans[i] , Ret[Target] ) ;
        if( Ec / (double) Ans[i].length() <= Th )
            return 1 ;
    }
    return 0 ;
}
double CalTh( )
{
    double MinTh , RetTh = 10000000.0 ;
    for( int i = 0 ; i < RetSz ; i++ )
    {
        MinTh = 10000000.0 ;
        for( int j = 0 ; j < AnsSz ; j++ )
            MinTh = min( MinTh , (double)EditDis( Ret[i] , Ans[j] ) / (double)Ans[j].length() ) ;
        //printf( "%d: %lf\n" , i , MinTh ) ;
        RetTh += MinTh ;
        //RetTh = min( RetTh , MinTh ) ;
    }
    return RetTh / (double)RetSz ;
    //return RetTh ;
}
int main( int argc , char *argv[ ] )
{
    if( argc != 3 )
    {
        printf( "Parameters Error!\n" ) ;
        printf( "Usage: ./a.out Yor_Ans.txt  Correct_Ans.txt\n" ) ;
        return 0 ;
    }
    //Th = (double) atof( argv[3] ) ;
    double SinglePre ;
    // 1:Ret  2:Ans
    ReadFiles( argv[1] , argv[2] ) ;
    SingleMap = 0.0 ;
    MatchCnt  = 0.0 ;
    Th = CalTh( ) ;
    printf( "%.4lf\n" , Th ) ;
    for( int i = 0 ; i < RetSz ; i++ )
        if( CheckMatch( i ) )
        {
            MatchCnt += 1.0 ;
            //printf( "%.2lf\n" , MatchCnt / (double)(i+1) ) ;
            SinglePre += MatchCnt / (double)(i+1) ;
        }
    SingleMap = SinglePre / (double)AnsSz ;
    printf( "%.2lf / %.2lf / %.2lf , (%d,%d)\n" , SingleMap , SinglePre , MatchCnt , RetSz ,  AnsSz ) ;
    printf( "MAP %.2lf\n" , SingleMap ) ;
    printf( "Acc %.2lf / Recall %.2lf\n" , MatchCnt/RetSz , MatchCnt/AnsSz ) ;
    return 0 ;
}
