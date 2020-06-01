list_for_N = [1,6,11,16,21,26,31,36,41,46,51,56]
list_for_E = [2,7,12,17,22,27,32,37,42,47,52,57]
list_for_O = [3,8,13,18,23,28,33,38,43,48,53,58]
list_for_A = [4,9,14,19,24,29,34,39,44,49,54,59]
list_for_C = [5,10,15,20,25,30,35,40,45,50,55,60]
QuestionReversed = [1,16,31,46,12,27,42,57,3,8,18,23,33,38,48,9,14,24,29,39,44,54,59,15,30,45,55]

RawScoresDict = {}
Rscores = {}
Tscores = {}
male_or_female = ""
name = ""


def giveScoresRaw(que_no, answer):
	if que_no in QuestionReversed:
		answer = 6-answer
		RawScoresDict[que_no] = answer
	else:
		RawScoresDict[que_no] = answer

def calcTscore():
	if male_or_female == "male":
		N_score_Dist = 0.7142857
		E_score_Dist = 0.55555555
		O_score_Dist = 0.55555555
		A_score_Dist = 0.5
		C_score_Dist = 0.55555555

		N_sub_val = 1
		E_sub_val = 13.777777
		O_sub_val = 13.777777
		A_sub_val = 19.5
		C_sub_val = 19.444444
	else:
		N_score_Dist = 1
		E_score_Dist = 0.555555556
		O_score_Dist = 0.58823529
		A_score_Dist = 0.47619047
		C_score_Dist = 0.58823529

		N_sub_val = -2
		E_sub_val = 14.4444444
		O_sub_val = 11.4705846
		A_sub_val = 21.6666
		C_sub_val = 20.29

	Tscores["N"] = int((Rscores["N"]-N_sub_val)/N_score_Dist)+25
	Tscores["E"] = int((Rscores["E"]-E_sub_val)/E_score_Dist)+25
	Tscores["O"] = int((Rscores["O"]-O_sub_val)/O_score_Dist)+25
	Tscores["A"] = int((Rscores["A"]-A_sub_val)/A_score_Dist)+25
	Tscores["C"] = int((Rscores["C"]-C_sub_val)/C_score_Dist)+25

	for k in Tscores:
		if Tscores[k]>74:
			Tscores[k]=74


def CalcScores():
	sum = 0
	for i in list_for_N:
		sum = sum + RawScoresDict[i]
	Rscores["N"] = sum

	sum = 0
	for i in list_for_E:
		sum = sum + RawScoresDict[i]
	Rscores["E"] = sum

	sum = 0
	for i in list_for_O:
		sum = sum + RawScoresDict[i]
	Rscores["O"] = sum

	sum = 0
	for i in list_for_A:
		sum = sum + RawScoresDict[i]
	Rscores["A"] = sum

	sum = 0
	for i in list_for_C:
		sum = sum + RawScoresDict[i]
	Rscores["C"] = sum

	
	
if __name__ =="__main__":
	print("Welcome to the NEO FIVE FACTOR SCORING")
	print("Enter Name:")
	name = str(input())
	print("male_or_female:")
	male_or_female = str(input())
	for i in range(1,61):
		print("Enter the answer for question no:" + str(i))
		answer = int(input())
		giveScoresRaw(i,answer)
	print("The scores are :")
	print(RawScoresDict)
	CalcScores()
	calcTscore()
	print(name + " and " + male_or_female)
	print("The R scores are :")
	print(Rscores)
	print("The T scores are :")
	print(Tscores)
