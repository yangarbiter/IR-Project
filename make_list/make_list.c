#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <math.h>
#include "porter.c"

typedef struct
{
    char voc[100];
    char o_voc[100];
    double tf;
    double df;
    double prob;
    int link;
}term_t;
term_t *term;
int now_term = 0, max_term = 100;

char sentence[10000];
char original_word[100];
char corpus_list[150000][100];
double corpus_df[150000];
int corpus_cnt = 0;
char stopword_list[150000][100];
int stopword_cnt = 0;

int cmp(const void *a, const void *b)
{
    term_t *termA = (term_t*)a;
    term_t *termB = (term_t*)b;
    if(termA->prob >= termB->prob)
        return 1;
    else
        return -1;
}
double is_stopword(char *str)
{
    int i;
    for(i = 0 ; i < stopword_cnt ; i++)
	if(strcmp(str , stopword_list[i]) == 0 )
	    return 1;
    return 0;
}
void parse_xml(char* str)
{
    char *tmp;
    int i, flag, tmplen = 0;
    tmp = malloc(65536*sizeof(char));
    for(i = 0; i < strlen(str); i++)
    {
	if(str[i] == '<')
		flag = 1;
        else if(str[i] == '>')
		flag = 0;
	if(flag == 0)	
            tmp[tmplen++] = str[i];
    }
    strcpy(str, tmp);
    free(tmp);
}
double find_df(char *str)
{
    int i;
    for(i = 0 ; i < corpus_cnt ; i++)
        if(strcmp(str , corpus_list[i]) == 0 )
            return corpus_df[i]+1;
    return 1;
}
void to_sentence(char* str)
{
    char *tmp;
    int i, tmplen = 0;
    tmp = malloc(65536*sizeof(char));
    for(i = 0; i < strlen(str); i++)
        if(LETTER(str[i]))
            tmp[tmplen++] = str[i];
        else
	    tmp[tmplen++] = ' ';
    tmp[tmplen] = '\0';
    strcpy(str, tmp);
    free(tmp);
}

int to_valid_word(char* str)
{
    //printf("%s\n", str);
    char tmp[100], flag = 1;
    int i, tmplen = 0;
    for(i = 0; i < strlen(str); i++)
    {
            if(str[i]-'A' < 26 && str[i]-'A' >= 0)
                str[i] = tolower(str[i]);
            else
                flag = 0;
    }

    for(i = 0; i < strlen(str); i++)
        if(LETTER(str[i]) || (str[i] == '-' && tmplen != 0))
            tmp[tmplen++] = str[i];
    tmp[tmplen] = '\0';
    strcpy(str, tmp);
    strcpy(original_word, tmp);
    stemfile(str);
    //printf("%s \n", s);
    if(is_stopword(s))
   // {
	//printf("%s is stopword\n", s);
	return 0;
    //}
    if(flag == 0 && strlen(s) <=4)
        return 0;
    return 1;

}

int main(int argc, char * argv[])
{
    int i, num, j, k;
    char str[100], new_str[100], tagger[30];
    char *buf;
    buf = malloc(65536*sizeof(char));
    s = (char *) malloc(i_max+1);
    double k1 = 0.01;

    //generate pipes
    int read_fd[2], write_fd[2];
    FILE *read_fp, *write_fp;
    if(pipe(write_fd) !=0 )
    {
			fprintf(stderr,"pipe(write_fd)  error\n");
			return 1;
    }
    if(pipe(read_fd) !=0 )
    {
        fprintf(stderr,"pipe(read_fd)  error\n");
        return 1;
    }
    if(fork() == 0)
    {
			dup2(read_fd[1], STDOUT_FILENO);
			dup2(write_fd[0], STDIN_FILENO);
			close(read_fd[1]);
			close(write_fd[0]);
			execl(argv[1],argv[1], (char*)0);
			fprintf(stderr,"fork  error\n");
			exit(127);
    }
    write_fp = fdopen(write_fd[1],"w");
    if(write_fp == NULL)
    {
        fprintf(stderr,"fdopen write[1] error\n");
        return 1;
    }
    read_fp= fdopen(read_fd[0],"r");
    if(read_fp == NULL)
    {
        fprintf(stderr,"fdopen read_fd[0] error\n");
        exit(0);
    }


    FILE* corpus_fp = fopen(argv[2], "r");
    if(corpus_fp == NULL)
    {
        printf("cannot open the corpus");
        return 1;
    }

    while(fscanf(corpus_fp, "%s %d", str, &num) != EOF)
    {
        strcpy(corpus_list[corpus_cnt], str);
        corpus_df[corpus_cnt] = num;
        corpus_cnt++;
    }
    fclose(corpus_fp);

    FILE* stopword_fp = fopen(argv[3], "r");
    if(stopword_fp == NULL)
    {
        printf("cannot open the stopword");
        return 1;
    }

    while(fscanf(stopword_fp, "%s", str) != EOF)
    {
        strcpy(stopword_list[stopword_cnt], str);
        stopword_cnt++;
    }
    fclose(stopword_fp);
   // for(i = 0 ; i < stopword_cnt; i++)
//	fprintf(stderr, "%s\n", stopword_list[i]);



    term = malloc(100*sizeof(term_t));
    //preprocess the background information
    //scanf("%s", str);//the background information file name
    FILE *fp = fopen(argv[4], "r");
    if(fp == NULL)
    {
        printf("cannot open the file");
        return 1;
    }
    for(j = 0; j < 3; j++)
    {
         if(j ==1)
         {
         	fgets(str, 100, fp);
        	 for(i = 0 ; i < strlen(str) ; i++)
			if(str[i] == ' ' && str[i-1] == ':')
				break;
		i++;
         	for(k = 0 ; k+i < strlen(str); k++)
			str[k] = str[i+k];
                str[k-1] = '\0';
                strcpy(term[0].voc,str);
                strcpy(term[0].o_voc,str);
                term[0].tf = 1;
                term[0].link = 0;
		term[0].prob = 0.3;
                now_term++;
		
	 }
         else
	{
         fgets(buf, 65536, fp);
	 parse_xml(buf);
	//printf("%s\n", buf);
         while(sscanf(buf,"%s", str)!=EOF)
         {
            	buf+=strlen(str);
                if(to_valid_word(str) == 0)
                    continue;
                //printf("%s is OK\n",s);

                for(i = 0; i < now_term ; i++)
                    if(strcmp(term[i].voc , s) == 0)
                        break;
                if(i == now_term)
                {
                    if(now_term >= max_term)
                    {
                        max_term *=2;
                        term = realloc(term , max_term*sizeof(term_t));
                    }
                    strcpy(term[i].voc,s);
                    strcpy(term[i].o_voc, original_word);
                    if(tagger[0] == 'N' && tagger[1] == 'N')
                    {
			//if(tagger[2] == 'P')
                          //  term[i].prob = 0.3;
			//else
                            term[i].prob = 0.15;
                    }
                    else
                        term[i].prob = 0.01;
                    now_term++;
                    term[i].tf = 1;
                    term[i].link = 0;
                    term[i].df = find_df(s);
                    //printf("df =%lf\n", term[i].df);
                    term[i].prob+= (log(550/term[i].df)*k1);
                }
                //else
                //{
                  //  term[i].tf++;
                    //term[i].prob+= (log(term[i].df)*k1);
                // }
                //if s isn't in the common word list
   	 }   
	}
    }

    fclose(fp);
    
    while(1)
    {
        fgets(buf, 65536, stdin);
        {
            //printf("string = %s", buf);
            to_sentence(buf);
            //printf("%s\n", buf);
            fprintf(write_fp, "%s\n", buf);
            fflush(write_fp);
            fgets(buf, 65536, read_fp);
	    //printf("string = %s", buf);
            while(sscanf(buf,"%s %s", str, tagger)!=EOF)
            {
		//printf("str = %s\n", str);
                buf+=(strlen(str)+strlen(tagger)+2);
		//printf("len %d le %d \n", strlen(str), strlen(tagger));
                if(to_valid_word(str) == 0)
                    continue;
                //printf("%s is OK\n",s);

                for(i = 0; i < now_term ; i++)
                    if(strcmp(term[i].voc , s) == 0)
                        break;
                if(i == now_term)
                {
                    if(now_term >= max_term)
                    {
                        max_term *=2;
                        term = realloc(term , max_term*sizeof(term_t));
                    }
                    strcpy(term[i].voc,s);
                    strcpy(term[i].o_voc, original_word);
                    if(tagger[0] == 'N' && tagger[1] == 'N')
                    {
			//if(tagger[2] == 'P')
                          //  term[i].prob = 0.3;
			//else
                            term[i].prob = 0.15;
                    }
                    else
                        term[i].prob = 0.01;
                    now_term++;
                    term[i].tf = 1;
                    term[i].link = 0;
                    term[i].df = find_df(s);
                    //printf("df =%lf\n", term[i].df);
                    term[i].prob+= (log(550/term[i].df)*k1);
                }
                //else
                //{
                  //  term[i].tf++;
                    //term[i].prob+= (log(term[i].df)*k1);
                // }
                //if s isn't in the common word list
            }

            qsort(term, now_term, sizeof(term_t), cmp);
            for(i = now_term-1; i>=0 && term[i].prob >=0.2 ; i--)
               printf("%s\n", term[i].o_voc);
	    //printf("****************an iteraion ends*******************\n"); 
        }
    }

    free(s);
    free(term);
    free(buf);

    return 0;
}