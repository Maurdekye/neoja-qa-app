import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'pages/questions_list_page.dart';
import 'services/api_service.dart';
import 'services/socket_service.dart';
import 'pages/question_detail_page.dart';

void main() {
  const apiUrl = const String.fromEnvironment('FLASK_API_BASE_URL', defaultValue: 'http://localhost:5000');
  
  runApp(MyApp(apiUrl));
}

class MyApp extends StatelessWidget {
  final String apiUrl;

  MyApp(this.apiUrl);

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        Provider<APIService>(
          create: (_) => APIService(apiUrl),
        ),
        ChangeNotifierProvider<SocketService>(
          create: (_) => SocketService(apiUrl),
        ),
      ],
      child: MaterialApp(
        title: 'Neoja Q&A App',
        theme: ThemeData(primarySwatch: Colors.blue),
        initialRoute: '/',
        routes: {
          '/': (context) => QuestionsListPage(),
        },
        onGenerateRoute: (settings) {
          if (settings.name == '/questionDetail') {
            final questionId = settings.arguments as String;
            return MaterialPageRoute(
              builder: (context) => QuestionDetailPage(questionId: questionId),
            );
          }
          return null;
        },
      ),
    );
  }
}
