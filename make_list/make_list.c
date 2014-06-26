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
#define STR_LENGTH 100
#define BUF_SIZE 65536
#define CORPUS_SIZE 150000
#define DOC_NUM 550

typedef struct
{
	char voc[STR_LENGTH];// the stemmed word
	char o_voc[STR_LENGTH];//the word before stemming
	double tf;//term frequency
	double df;//document frequency 
	double weight;//term weight
	int link;//0: appear in the speech ; 1: appear in the related website
}term_t;
term_t *term;
int now_term = 0, max_term = 100;

char sentence[BUF_SIZE];
char original_word[STR_LENGTH];
char corpus_list[CORPUS_SIZE][STR_LENGTH];
double corpus_df[CORPUS_SIZE];
int corpus_cnt = 0;
char stopword_list[CORPUS_SIZE][STR_LENGTH];
int stopword_cnt = 0;
double k5 = 0.5;
int cmp(const void *a, const void *b)// use for sorting weights
{
	term_t *termA = (term_t*)a;
	term_t *termB = (term_t*)b;
	if(termA->weight > termB->weight)
		return 1;
	else
		return -1;
}
double is_stopword(char *str)//whether the word is a stopword
{
	int i;
	for(i = 0 ; i < stopword_cnt ; i++)
		if(strcmp(str , stopword_list[i]) == 0 )
			return 1;
	return 0;
}
void parse_html_tag(char* str)//parse <>, </>
{
	char *tmp;
	int i, flag = 0, tmplen = 0;
	tmp = malloc(BUF_SIZE*sizeof(char));
	for(i = 0; i <= strlen(str); i++)
	{
		if(str[i] == '<')
			flag = 1;
		else if(str[i] == '>')
		{
			flag = 0;
			continue;
		}
		if(flag == 0)
			tmp[tmplen++] = str[i];
	}
	//printf("str = %s", str);
	//printf("tmp = %s", tmp);
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
void to_sentence(char* str)//remove all the non-letter char
{
	char *tmp;
	int i, tmplen = 0;
	tmp = malloc(BUF_SIZE*sizeof(char));
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
	char tmp[STR_LENGTH], flag = 1;
	int i, tmplen = 0;
	for(i = 0; i < strlen(str); i++)
		if(LETTER(str[i]) || (str[i] == '-' && tmplen != 0))
			tmp[tmplen++] = str[i];
	tmp[tmplen] = '\0';
	strcpy(original_word, tmp);
	for(i = 0; i < strlen(tmp); i++)
	{
			if(tmp[i]-'A' < 26 && tmp[i]-'A' >= 0)
				tmp[i] = tolower(tmp[i]);
			else
				flag = 0;
	}
	strcpy(str, tmp);
	stemstring(str);
	if(is_stopword(s))
		return 0;//will not be concerned
	if(flag == 0 && strlen(s) <=4)
		return 0;//will not be concerned
	return 1;

}
add_term(char* str, char* tagger, double tf_weight ,double idf_weight, double noun_weight, int link )
{
	int i;
	for(i = 0; i < now_term ; i++)
		if(strcmp(term[i].voc , str) == 0)
			break;
	if(i == now_term)
	{
		if(now_term >= max_term)
		{
			max_term *=2;
			term = realloc(term , max_term*sizeof(term_t));
		}
		strcpy(term[i].voc, str);
		strcpy(term[i].o_voc, original_word);
		if(tagger[0] == 'N' && tagger[1] == 'N')
		{
				//if(tagger[2] == 'P')
					//  term[i].weight = 0.3;
				//else
				term[i].weight =  noun_weight;
		}
		else
			term[i].weight = 0.01;
		now_term++;
		term[i].tf = 1;
		term[i].link = link;
		term[i].df = find_df(str);
		term[i].weight+= ( log(  (DOC_NUM-term[i].df+0.5)/(term[i].df+0.5)  )  *idf_weight);
		}
		if(link ==1)
			term[i].weight *= k5;
	else
	{
		term[i].tf++;
		if(link == 0)
			term[i].weight+= ( log(  (DOC_NUM-term[i].df+0.5)/(term[i].df+0.5)  )  *idf_weight * tf_weight) ;
		else
			term[i].weight+= ( log(  (DOC_NUM-term[i].df+0.5)/(term[i].df+0.5)  )  *idf_weight * tf_weight * k5) ;
	}
}

int main(int argc, char * argv[])
{
	int i, j, k, num;
	char str[STR_LENGTH], new_str[STR_LENGTH], tagger[STR_LENGTH];
	char *buf;
	buf = malloc(BUF_SIZE*sizeof(char));
	s = (char *) malloc(i_max+1);
	double filter = 0.23, k1 = 0.15, k2  = 0.02, k3 = 0.15, k4 = 0.01;
	//fprintf(stderr,"start init\n");
	if(argc < 5)
	{
		fprintf(stderr,"argument number error\n");
		return 1;
	}
	if(argc >= 11)
	{
		sscanf(argv[5], "%lf", &filter);
		sscanf(argv[6], "%lf", &k1);
		sscanf(argv[7], "%lf", &k2);
		sscanf(argv[8], "%lf", &k3);
		sscanf(argv[9], "%lf", &k4);
		sscanf(argv[10], "%lf", &k5);
	}
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
	//fprintf(stderr,"fork and exec ends\n");

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
	//fprintf(stderr,"reading corpus ends\n");
	
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
	//fprintf(stderr,"reading stopowrd_list ends\n");

	term = malloc(STR_LENGTH*sizeof(term_t));
	
	//preprocess the background information
	
	FILE *fp = fopen(argv[4], "r");	
	if(fp == NULL)
	{
		printf("cannot open the file");
		return 1;
	}
	for(j = 0; j < 4; j++)
	{
			// if(j ==1)
			// {
			//	fgets(str, STR_LENGTH, fp);
			//	 for(i = 0 ; i < strlen(str) ; i++)
			//	if(str[i] == ' ' && str[i-1] == ':')
			//		break;
			//	i++;
		//		for(k = 0 ; k+i < strlen(str); k++)
			//	str[k] = str[i+k];
			//		str[k-1] = '\0';
			//		strcpy(term[0].voc,str);
			//		strcpy(term[0].o_voc,str);
			//		term[0].tf = 1;
			//		term[0].link = 0;
			//		term[0].weight = 0.3;
			//		now_term++;
		//	}
			//else
			//{
		
		fgets(buf, BUF_SIZE, fp);
		//printf("buf = %s", buf);
		parse_html_tag(buf);
		//printf("rbuf = %s", buf);
		to_sentence(buf);
		//printf("rehhhabuf = %s", buf);
		fprintf(write_fp, "%s\n", buf);
		fflush(write_fp);
		fgets(buf, BUF_SIZE, read_fp);
		//printf("reabuf = %s", buf);
		while(sscanf(buf,"%s %s", str, tagger)!=EOF)
		{
			//fprintf(stderr,"LLadd %s\n", s);
			buf+=(strlen(str)+strlen(tagger)+2);
			if(to_valid_word(str) == 0)
				continue;
			
			add_term(s, tagger, k1, k2, k3, 1);
		} 	
		//}
	}
	fclose(fp);
	qsort(term, now_term, sizeof(term_t), cmp);
	for(i = now_term-1; i>=0 && term[i].weight >= filter ; i--)
			  printf("%s\n", term[i].o_voc);
			//printf("%s %lf\n", term[i].o_voc, term[i].weight);
		//printf("***************HHHH***********\n"); 
	printf("\n");
	fflush(stdout);
	
	while(1)
	{
		fgets(buf, BUF_SIZE, stdin);
		//fprintf(stderr,"gets = %s", buf);
		if(buf[0] == '&')
		{
			for(i = 0 ; i < strlen(buf); i++)
				buf[i] = buf[i+1];
			sscanf(buf, "%s %s", str, new_str);
			if(to_valid_word(str) == 0)
					continue;
			for(i = 0; i < now_term ; i++)
				if(strcmp(term[i].voc , s) == 0)
					break;
			fprintf( stderr,"%s %s\n",s, new_str);
			if(i  < now_term)
			{
				//fprintf(stderr, "%s\n", s);
				if(new_str[0] == 'F')
					term[i].weight = k4;
				fprintf(stderr, "weight decreases to %lf\n", term[i].weight);
			}
		}
		else if(buf[0] == '*')
		{
			
			for(i = 0; i <= strlen(buf); i++)
				buf[i] = buf[i+1];
			to_sentence(buf);
			fprintf(write_fp, "%s\n", buf);
			fflush(write_fp);
			fgets(buf, BUF_SIZE, read_fp);
			while(sscanf(buf,"%s %s", str, tagger)!=EOF)
			{
				buf+=(strlen(str)+strlen(tagger)+2);
				if(to_valid_word(str) == 0)
					continue;
				//fprintf(stderr,"add %s\n", s);
				add_term(s, tagger, k1, k2, k3, 1);
			}
		}
		else
		{
			to_sentence(buf);
			fprintf(write_fp, "%s\n", buf);
			fflush(write_fp);
			fgets(buf, BUF_SIZE, read_fp);
			while(sscanf(buf,"%s %s", str, tagger)!=EOF)
			{
				buf+=(strlen(str)+strlen(tagger)+2);
				if(to_valid_word(str) == 0)
					continue;
				//fprintf(stderr,"add %s\n", s);
				add_term(s, tagger, k1, k2, k3, 0);
			}
		}
		qsort(term, now_term, sizeof(term_t), cmp);
		for(i = now_term-1; i>=0 && term[i].weight >= filter ; i--)
			  printf("%s\n", term[i].o_voc);
			//printf("%s %lf\n", term[i].o_voc, term[i].weight);
		//printf("***************HHHH***********\n"); 
		printf("\n");
		fflush(stdout);
	}

	free(s);
	free(term);
	free(buf);

	return 0;
}
